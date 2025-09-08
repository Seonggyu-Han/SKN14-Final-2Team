# --- stdlib ---
import json
import os
# --- typing ---
from typing import TypedDict, List, Optional, Dict, Any

# --- env ---
from dotenv import load_dotenv
from config import llm, embeddings, index, MODEL_NAME, pc


# --- langchain / langgraph ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

# --- services (쿼리 파싱/필터/검색/응답/가격 키워드) ---
from tools import run_llm_parser
from tools import apply_meta_filters
from tools import query_pinecone
from tools import generate_response
from tools import extract_price_search_keywords

# --- tools (Naver 가격/ML 추천) ---
from tools import price_tool, recommend_perfume_simple
load_dotenv()


SUPERVISOR_SYSTEM_PROMPT = """
You are the "Perfume Recommendation Supervisor (Router)". Analyze the user's query (Korean or English) and route to exactly ONE agent below.

[Agents]
- LLM_parser         : Parses/normalizes multi-facet queries (2+ product facets).
- FAQ_agent          : Perfume knowledge / definitions / differences / general questions.
- human_fallback     : Non-perfume or off-topic queries.
- price_agent        : Price-only intents (cheapest, price, buy, discount, etc.).
- ML_agent           : Single-preference recommendations (mood/season vibe like "fresh summer", "sweet", etc.).

[Facets to detect ("product facets")]
- brand            (e.g., Chanel, Dior, Creed)
- season           (spring/summer/fall/winter; "for summer/winter")
- gender           (male/female/unisex)
- sizes            (volume in ml: 30/50/100 ml)
- day_night_score  (day/night/daily/office/club, etc.)
- concentration    (EDT/EDP/Extrait/Parfum/Cologne)

[Price intent keywords (not exhaustive)]
- Korean: 가격, 얼마, 가격대, 구매, 판매, 할인, 어디서 사, 배송비
- English: price, cost, cheapest, buy, purchase, discount

[FAQ examples]
- Differences between EDP vs EDT, note definitions, longevity/projection, brand/line info.

[Single-preference (ML_agent) examples]
- "Recommend a cool perfume for summer", "Recommend a sweet scent", "One citrusy fresh pick"
  (= 0–1 of the above facets mentioned; primarily taste/mood/situation).


[Routing rules (priority)]
1) Non-perfume / off-topic → human_fallback
2) Pure price-only intent (no product facets mentioned) → price_agent
   e.g., "향수 가격 알려줘" → price_agent
3) Count product facets in the query:
   - If facets ≥ 2 → LLM_parser (can handle price intent within multi-facet queries)
   - If facets = 1 AND has price intent → LLM_parser (e.g., "샤넬 향수 가격")
4) Otherwise (single-topic queries):
   - Pure price query with specific brand/product → price_agent
   - Perfume knowledge/definitions → FAQ_agent
   - Single taste/mood recommendation → ML_agent
5) Tie-breakers:
   - If complex query (multiple aspects) → LLM_parser
   - If pure price intent → price_agent
   - Else: knowledge → FAQ_agent, taste → ML_agent

[Output format]
Return ONLY this JSON (no extra text):
{{
  "next": "<LLM_parser|FAQ_agent|human_fallback|price_agent|ML_agent>",
  "reason": "<one short English sentence>",
  "facet_count": <integer>,
  "facets": {{
    "brand": "<value or null>",
    "season": "<value or null>",
    "gender": "<value or null>",
    "sizes": "<value or null>",
    "day_night_score": "<value or null>",
    "concentration": "<value or null>"
  }},
  "scent_vibe": "<value if detected, else null>",
  "query_intent": "<price|faq|scent_pref|non_perfume|other>"
}}
""".strip()

# ---------- 1) State ----------
class AgentState(TypedDict):
    messages: List[BaseMessage]           # conversation log
    next: Optional[str]                   # routing decision key 
    router_json: Optional[Dict[str, Any]] # parsed JSON from router

router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SUPERVISOR_SYSTEM_PROMPT),
        ("user", "{query}")
    ]
)

def supervisor_node(state: AgentState) -> AgentState:
    """Call the router LLM and return parsed JSON + routing target."""
    user_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_query = m.content
            break
    if not user_query:
        user_query = "(empty)"

    chain = router_prompt | llm
    ai = chain.invoke({"query": user_query})
    text = ai.content

    # JSON strict parse
    chosen = "human_fallback"
    parsed: Dict[str, Any] = {}
    try:
        parsed = json.loads(text)
        maybe = parsed.get("next")
        if isinstance(maybe, str) and maybe in {"LLM_parser","FAQ_agent","human_fallback","price_agent","ML_agent"}:
            chosen = maybe
    except Exception:
        parsed = {"error": "invalid_json", "raw": text}

    msgs = state["messages"] + [AIMessage(content=text)]
    return {
        "messages": msgs,
        "next": chosen,
        "router_json": parsed
    }

# ---------- 4) Agent Nodes ----------
def LLM_parser_node(state: AgentState) -> AgentState:
    """실제 RAG 파이프라인을 실행하는 LLM_parser 노드 + 가격 검색 통합"""
    user_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_query = m.content
            break
    if not user_query:
        user_query = "(empty)"

    try:
        print(f"🔍 LLM_parser 실행: {user_query}")
        
        # 1단계: LLM으로 쿼리 파싱
        parsed_json = run_llm_parser(user_query)
        if "error" in parsed_json:
            error_msg = f"[LLM_parser] 쿼리 파싱 오류: {parsed_json['error']}"
            msgs = state["messages"] + [AIMessage(content=error_msg)]
            return {"messages": msgs, "next": None, "router_json": state.get("router_json")}
        
        # 2단계: 메타필터 적용
        filtered_json = apply_meta_filters(parsed_json)
        
        # 3단계: 쿼리 벡터화
        query_vector = embeddings.embed_query(user_query)
        
        # 4단계: Pinecone 검색
        search_results = query_pinecone(query_vector, filtered_json, top_k=5)
        
        # 5단계: 최종 응답 생성
        final_response = generate_response(user_query, search_results)
        
        # 6단계: 가격 의도 감지 및 가격 정보 추가
        price_keywords = ['가격', '얼마', '가격대', '구매', '판매', '할인', '어디서 사', '배송비', 'price', 'cost', 'cheapest', 'buy', 'purchase', 'discount']
        has_price_intent = any(keyword in user_query.lower() for keyword in price_keywords)
        
        if has_price_intent:
            # 검색된 향수들로부터 가격 검색용 키워드 추출
            price_search_keywords = extract_price_search_keywords(search_results, user_query, parsed_json)
            
            print(f"💰 가격 검색 키워드: {price_search_keywords}")
            print(f"🔍 검색된 향수 정보: {search_results.get('matches', [{}])[0].get('metadata', {}) if search_results.get('matches') else 'No matches'}")
            
            if price_search_keywords and price_search_keywords != "향수":
                try:
                    price_info = price_tool.invoke({"user_query": price_search_keywords})
                    
                    # 가격 정보를 최종 응답에 추가
                    final_response_with_price = f"""{final_response}

---

💰 **가격 정보**
{price_info}"""
                except Exception as price_error:
                    print(f"❌ 가격 검색 오류: {price_error}")
                    final_response_with_price = f"""{final_response}

---

💰 **가격 정보**
❌ 가격 검색 중 오류가 발생했습니다. 나중에 다시 시도해주세요."""
            else:
                final_response_with_price = f"""{final_response}

---

💰 **가격 정보**
🔍 구체적인 향수명이 필요합니다. 위 추천 향수들 중 원하는 제품명을 다시 검색해보세요."""
        else:
            final_response_with_price = final_response
        
        # 결과 요약
        summary = f"""[LLM_parser] RAG 파이프라인 완료 ✅

📊 파싱 결과: {json.dumps(parsed_json, ensure_ascii=False)}
🔍 필터링 결과: {json.dumps(filtered_json, ensure_ascii=False)}
🎯 검색된 향수 개수: {len(search_results.get('matches', []))}

💬 추천 결과:
{final_response_with_price}"""

        msgs = state["messages"] + [AIMessage(content=summary)]
        return {"messages": msgs, "next": None, "router_json": state.get("router_json")}
        
    except Exception as e:
        error_msg = f"[LLM_parser] RAG 파이프라인 실행 중 오류: {str(e)}"
        print(f"❌ LLM_parser 전체 오류: {e}")
        msgs = state["messages"] + [AIMessage(content=error_msg)]
        return {"messages": msgs, "next": None, "router_json": state.get("router_json")}
    
    
def human_fallback_node(state: AgentState) -> AgentState:
    """향수 관련 복잡한 질문에 대한 기본 응답"""
    user_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_query = m.content
            break
    if not user_query:
        user_query = "(empty)"
    
    fallback_response = (
        f"❓ '{user_query}' 더 명확한 설명이 필요합니다.\n"
        f"👉 질문을 구체적으로 다시 작성해 주세요.\n"
        f"💡 또는 향수에 관한 멋진 질문을 해보시는 건 어떨까요?"
    )
    
    msgs = state["messages"] + [AIMessage(content=fallback_response)]
    return {"messages": msgs, "next": None, "router_json": state.get("router_json")}

# ---------- 5) 직접 도구 호출 방식으로 에이전트 구현 ----------
def price_agent_node(state: AgentState) -> AgentState:
    """Price agent - 직접 도구 호출"""
    user_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_query = m.content
            break
    if not user_query:
        user_query = "(empty)"
    
    try:
        # 직접 price_tool 호출
        price_result = price_tool.invoke({"user_query": user_query})
        
        # 결과를 더 자연스럽게 포맷팅
        final_answer = f"💰 **가격 정보**\n\n{price_result}"
        
        msgs = state["messages"] + [AIMessage(content=final_answer)]
        return {
            "messages": msgs, 
            "next": None, 
            "router_json": state.get("router_json")
        }
    except Exception as e:
        error_msg = f"❌ 가격 조회 중 오류가 발생했습니다: {str(e)}"
        msgs = state["messages"] + [AIMessage(content=error_msg)]
        return {
            "messages": msgs, 
            "next": None, 
            "router_json": state.get("router_json")
        }

def FAQ_agent_node(state: AgentState) -> AgentState:
    """FAQ agent - LLM 기본 지식으로 향수 관련 질문 답변"""
    user_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_query = m.content
            break
    if not user_query:
        user_query = "(empty)"
    
    try:
        # LLM에게 향수 지식 전문가로서 답변하도록 프롬프트 설정
        faq_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 향수 전문가입니다. 사용자의 향수 관련 질문에 대해 정확하고 유용한 정보를 제공해주세요.

다음과 같은 주제들에 대해 답변할 수 있습니다:
- 향수의 종류와 농도 (EDT, EDP, Parfum 등)
- 향료와 노트에 대한 설명
- 브랜드별 특징과 대표 향수
- 향수 사용법과 보관법
- 계절별, 상황별 향수 선택 팁
- 향수의 지속력과 확산력

답변은 친근하고 이해하기 쉽게, 그리고 실용적인 조언을 포함해서 해주세요."""),
            ("user", "{question}")
        ])
        
        chain = faq_prompt | llm
        result = chain.invoke({"question": user_query})
        
        # 결과를 포맷팅
        final_answer = f"📚 **향수 지식**\n\n{result.content}"
        
        msgs = state["messages"] + [AIMessage(content=final_answer)]
        return {
            "messages": msgs, 
            "next": None, 
            "router_json": state.get("router_json")
        }
    except Exception as e:
        error_msg = f"❌ 향수 지식 답변 생성 중 오류가 발생했습니다: {str(e)}"
        msgs = state["messages"] + [AIMessage(content=error_msg)]
        return {
            "messages": msgs, 
            "next": None, 
            "router_json": state.get("router_json")
        }

def ML_agent_node(state: AgentState) -> AgentState:
    """ML agent - recommend_perfume_simple 도구 호출 후, LLM이 설명문 생성까지 수행"""
    user_query = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_query = m.content
            break
    if not user_query:
        user_query = "(empty)"

    try:
        # 1) ML 도구 호출 (구조화 데이터 보존)
        ml_result = recommend_perfume_simple.invoke({"user_text": user_query})
        # 예상 구조: {"recommendations": [...], "predicted_labels": [...]}
        ml_json_str = json.dumps(ml_result, ensure_ascii=False)

        # 2) LLM에 컨텍스트로 전달하여 자연어 답변 생성
        system_prompt = (
            "너는 향수 추천 설명가야. 아래 JSON은 ML 모델의 추천 결과이니, "
            "그 정보만 근거로 간결하고 친절한 한국어 답변을 만들어라.\n"
            "- 사용자의 질문 의도에 맞춰 Top 3를 핵심 이유와 함께 요약\n"
            "- 예측된 향 특성이 있으면 한 줄로 보여주기\n"
            "- 비슷한 대안 2개 정도와 다음 행동(예: 시즌/시간/지속력 선호 질문) 제안\n"
            "- 과장하거나 JSON에 없는 사실은 추측하지 말기"
        )
        human_prompt = (
            f"사용자 질문:\n{user_query}\n\n"
            f"ML 추천 JSON:\n```json\n{ml_json_str}\n```"
        )

        llm_out = llm.invoke([SystemMessage(content=system_prompt),
                              HumanMessage(content=human_prompt)])

        # 3) 최종 답변을 대화에 추가
        msgs = state["messages"] + [AIMessage(content=llm_out.content)]
        return {
            "messages": msgs,
            "next": None,
            "router_json": state.get("router_json")
        }

    except Exception as e:
        error_msg = f"❌ ML 추천 생성 중 오류가 발생했습니다: {str(e)}"
        msgs = state["messages"] + [AIMessage(content=error_msg)]
        return {
            "messages": msgs,
            "next": None,
            "router_json": state.get("router_json")
        }
# ---------- 7) Build Graph ----------
graph = StateGraph(AgentState)

# 노드 추가
graph.add_node("supervisor", supervisor_node)
graph.add_node("LLM_parser", LLM_parser_node)
graph.add_node("FAQ_agent", FAQ_agent_node)
graph.add_node("human_fallback", human_fallback_node)
graph.add_node("price_agent", price_agent_node)
graph.add_node("ML_agent", ML_agent_node)

# 시작점 설정
graph.set_entry_point("supervisor")

# 조건부 라우팅 함수
def router_edge(state: AgentState) -> str:
    return state["next"] or "human_fallback"

# 조건부 엣지 추가 (supervisor에서 각 agent로)
graph.add_conditional_edges(
    "supervisor",
    router_edge,
    {
        "LLM_parser": "LLM_parser",
        "FAQ_agent": "FAQ_agent",
        "human_fallback": "human_fallback",
        "price_agent": "price_agent",
        "ML_agent": "ML_agent",
    },
)

# 각 에이전트에서 END로 가는 엣지 추가
for node in ["LLM_parser", "FAQ_agent", "human_fallback", "price_agent", "ML_agent"]:
    graph.add_edge(node, END)

# 그래프 컴파일
app = graph.compile()


TEST_QUERIES = [
    "입생로랑 여성용 50ml 겨울용 향수 추천해줘.가격도 알려줘",                 
    "디올 EDP로 가을 밤(야간)에 쓸 만한 향수 있어?",                
    "EDP랑 EDT 차이가 뭐야?",                                       
    "탑노트·미들노트·베이스노트가 각각 무슨 뜻이야?",               
    "오늘 점심 뭐 먹을까?",                                         
    "오늘 서울 날씨 어때?",                                         
    "샤넬 넘버5 50ml 가격 알려줘.",                               
    "디올 소바쥬 가격 얼마야? 어디서 사는 게 제일 싸?",             
    "여름에 시원한 향수 추천해줘.",                                 
    "달달한 향 추천해줘.",
    "바보같은향 추천해줘"
]

def run_tests():
    for q in TEST_QUERIES:
        print("="*80)
        print("Query:", q)
        init: AgentState = {
            "messages": [HumanMessage(content=q)],
            "next": None,
            "router_json": None
        }
        try:
            out = app.invoke(init)
            ai_msgs = [m for m in out["messages"] if isinstance(m, AIMessage)]
            router_raw = ai_msgs[-2].content if len(ai_msgs) >= 2 else "(no router output)"
            agent_summary = ai_msgs[-1].content if ai_msgs else "(no agent output)"
            print("Router JSON:", router_raw)
            print("Agent summary:", agent_summary)
        except Exception as e:
            print(f"Error processing query: {e}")

def run_single_query(query: str):
    """단일 쿼리 테스트"""
    print(f"🔍 Query: {query}")
    print("-" * 50)
    
    init: AgentState = {
        "messages": [HumanMessage(content=query)],
        "next": None,
        "router_json": None
    }
    
    try:
        out = app.invoke(init)
        ai_msgs = [m for m in out["messages"] if isinstance(m, AIMessage)]
        
        if len(ai_msgs) >= 2:
            print("🤖 Router Decision:")
            print(ai_msgs[-2].content)
            print("\n📝 Final Response:")
            print(ai_msgs[-1].content)
        elif len(ai_msgs) == 1:
            print("📝 Response:")
            print(ai_msgs[-1].content)
        else:
            print("❌ No response generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # 환경 변수 확인
    print("🔧 환경 변수 확인:")
    print(f"OPENAI_API_KEY: {'✅ 설정됨' if os.getenv('OPENAI_API_KEY') else '❌ 미설정'}")
    print(f"PINECONE_API_KEY: {'✅ 설정됨' if os.getenv('PINECONE_API_KEY') else '❌ 미설정'}")
    print(f"NAVER_CLIENT_ID: {'✅ 설정됨' if os.getenv('NAVER_CLIENT_ID') else '❌ 미설정'}")
    print(f"NAVER_CLIENT_SECRET: {'✅ 설정됨' if os.getenv('NAVER_CLIENT_SECRET') else '❌ 미설정'}")
    print()
    
    print("🚀 향수 추천 시스템 테스트 시작...")
    print()
    
    # 개별 테스트용 함수 제공
    print("📋 사용 가능한 함수:")
    print("- run_tests(): 모든 테스트 쿼리 실행")
    print("- run_single_query('your query'): 단일 쿼리 테스트")
    print()
if __name__ == "__main__":
    ...
    print("🚀 향수 추천 시스템 테스트 시작...")
    print()
    
    # 개별 테스트용 함수 제공
    print("📋 사용 가능한 함수:")
    print("- run_tests(): 모든 테스트 쿼리 실행")
    print("- run_single_query('your query'): 단일 쿼리 테스트")
    print()

    # 🔽 이 부분 추가
    run_tests()  
