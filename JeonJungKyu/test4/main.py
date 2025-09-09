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
import re, json

BRAND_ALIASES = BRAND_ALIASES = {
    "겔랑": ["겔랑", "게랑", "Guerlain"],
    "구찌": ["구찌", "Gucci"],
    "끌로에": ["끌로에", "끌로 에", "Chloé", "Chloe"],
    "나르시소 로드리게즈": ["나르시소로드리게즈", "나르시소 로드리게즈", "나르시소", "로드리게즈", "Narciso Rodriguez"],
    "니샤네": ["니샤네", "Nishane"],
    "도르세": ["도르세", "도 르세", "D’ORSAY", "D'ORSAY", "DORSAY"],
    "디올": ["디올", "크리스찬디올", "크리스찬 디올", "Dior", "Christian Dior"],
    "딥티크": ["딥티크", "Diptyque"],
    "랑콤": ["랑콤", "Lancôme", "Lancome"],
    "로라 메르시에": ["로라메르시에", "로라 메르시에", "Laura Mercier"],
    "로에베": ["로에베", "Loewe"],
    "록시땅": ["록시땅", "록시탕", "록 시땅", "L’Occitane", "L'Occitane", "LOccitane", "L’Occitane en Provence"],
    "르 라보": ["르라보", "르 라보", "Le Labo"],
    "메모": ["메모", "Memo", "Memo Paris"],
    "메종 마르지엘라": ["메종마르지엘라", "메종 마르지엘라", "마르지엘라", "Maison Margiela"],
    "메종 프란시스 커정": ["메종프란시스커정", "메종 프란시스 커정", "프란시스 커정", "엠에프케이", "MFK", "Maison Francis Kurkdjian"],
    "멜린앤게츠": ["멜린앤게츠", "말린앤게츠", "멜린 앤 게츠", "Malin+Goetz", "Malin and Goetz", "Malin & Goetz"],
    "미우미우": ["미우미우", "미우 미우", "Miu Miu"],
    "바이레도": ["바이레도", "Byredo"],
    "반클리프 아펠": ["반클리프아펠", "반클리프 아펠", "반클리프앤아펠", "Van Cleef & Arpels", "Van Cleef and Arpels", "VCA"],
    "버버리": ["버버리", "Burberry"],
    "베르사체": ["베르사체", "Versace"],
    "불가리": ["불가리", "벌가리", "Bulgari", "BVLGARI"],
    "비디케이": ["비디케이", "BDK", "BDK Parfums"],
    "산타 마리아 노벨라": ["산타마리아노벨라", "산타 마리아 노벨라", "노벨라", "Santa Maria Novella", "SMN"],
    "샤넬": ["샤넬", "Chanel"],
    "세르주 루텐": ["세르주루텐", "세르주 루텐", "Serge Lutens"],
    "시슬리 코스메틱": ["시슬리", "시슬리코스메틱", "시슬리 코스메틱", "Sisley", "Sisley Paris"],
    "아쿠아 디 파르마": ["아쿠아디파르마", "아쿠아 디 파르마", "Acqua di Parma", "AdP"],
    "에따 리브르 도량쥬": ["에따리브르도랑쥬", "에따 리브르 도량쥬", "에따리브르", "Etat Libre d’Orange", "Etat Libre d'Orange", "ELDO"],
    "에르메스": ["에르메스", "Hermès", "Hermes"],
    "에스티 로더": ["에스티로더", "에스티 로더", "Estee Lauder", "Estée Lauder"],
    "엑스 니힐로": ["엑스니힐로", "엑스 니힐로", "Ex Nihilo"],
    "이니시오 퍼퓸": ["이니시오", "이니시오 퍼퓸", "Initio", "Initio Parfums Prives"],
    "이솝": ["이솝", "Aesop"],
    "입생로랑": ["입생로랑", "입 생로랑", "이브생로랑", "이브 생 로랑", "생로랑", "YSL", "Yves Saint Laurent", "Saint Laurent"],
    "제르조프": ["제르조프", "Xerjoff"],
    "조 말론": ["조말론", "조 말론", "Jo Malone", "Jo Malone London", "JML"],
    "조르지오 아르마니": ["조르지오아르마니", "조르지오 아르마니", "아르마니", "Giorgio Armani", "Armani"],
    "줄리엣 헤즈 어 건": ["줄리엣헤즈어건", "줄리엣 헤즈 어 건", "Juliette Has A Gun", "JHAG"],
    "지방시": ["지방시", "Givenchy"],
    "질 스튜어트": ["질스튜어트", "질 스튜어트", "Jill Stuart"],
    "크리드": ["크리드", "Creed"],
    "킬리안": ["킬리안", "Kilian", "Kilian Paris"],
    "톰 포드": ["톰포드", "톰 포드", "톰포 드", "톰 포 드", "Tom Ford"],
    "티파니앤코": ["티파니앤코", "티파니 앤 코", "티파니", "Tiffany & Co.", "Tiffany and Co.", "Tiffany"],
    "퍼퓸 드 말리": ["퍼퓸드말리", "퍼퓸 드 말리", "말리", "Parfums de Marly", "PDM"],
    "펜할리곤스": ["펜할리곤스", "펜할리곤즈", "Penhaligon’s", "Penhaligon's", "Penhaligons"],
    "프라다": ["프라다", "Prada"],
    "프레데릭 말": ["프레데릭말", "프레데릭 말", "Frederic Malle", "Frédéric Malle"],
}
CONC_SYNONYMS = {
    "오 드 퍼퓸": ["오 드 퍼퓸", "오드퍼퓸", "EDP", "eau de parfum"],
    "오 드 뚜왈렛": ["오 드 뚜왈렛", "오드뚜왈렛", "EDT", "eau de toilette"],
    "오 드 꼴로뉴": ["오 드 꼴로뉴", "EDC", "eau de cologne"],
    "파르펭": ["파르펭", "Parfum", "Extrait", "Extrait de Parfum"],
}

def _normalize_size(size_val):
    """'50' -> '50ml', '50 ml' -> '50ml'"""
    if not size_val:
        return None
    s = str(size_val).strip().lower().replace(" ", "")
    if s.endswith("ml"):
        return s
    if re.fullmatch(r"\d{1,4}", s):
        return s + "ml"
    return s

def _expand_brand(brand):
    if not brand:
        return []
    return BRAND_ALIASES.get(brand, [brand])

def _expand_concentration(conc):
    if not conc:
        return []
    c = str(conc)
    for k, syns in CONC_SYNONYMS.items():
        if k.replace(" ", "") in c.replace(" ", "") or c in syns:
            return syns
    return [c]

def _extract_matches(search_results: dict):
    """Pinecone matches -> list of metadata dict"""
    matches = (search_results or {}).get("matches") or []
    return [m.get("metadata") or {} for m in matches]

def _make_display_name(meta, size=None):
    brand = (meta.get("brand") or "").strip()
    name  = (meta.get("name") or "").strip()
    conc  = (meta.get("concentration") or "").strip()
    toks = [brand, name, conc, size]
    return " ".join([t for t in toks if t])

def build_item_queries_from_vectordb(
    search_results: dict,
    facets: dict | None = None,
    top_n_items: int = 5,
) -> list[dict]:
    """
    반환: [{item_label, queries}] 리스트
    - item_label: 사용자에게 보여줄 라벨(brand name conc size)
    - queries: 이 아이템만을 겨냥한 네이버 검색 후보들(문자열 리스트)
    (※ 브랜드+제품명 필수. 다른 제품으로 샐 여지를 최소화)
    """
    facets = facets or {}
    target_size = _normalize_size(facets.get("sizes"))
    metas = _extract_matches(search_results)[:top_n_items]

    results = []
    seen_items = set()  # (brand|name)로 중복 제거

    for meta in metas:
        brand = meta.get("brand")
        name  = meta.get("name")
        conc  = meta.get("concentration")
        sizes = meta.get("sizes")

        if not brand or not name:
            continue

        key = f"{brand}|{name}"
        if key in seen_items:
            continue
        seen_items.add(key)

        size_for_query = target_size
        if not size_for_query:
            if isinstance(sizes, (list, tuple)) and sizes:
                if "50" in sizes or "50ml" in sizes:
                    size_for_query = "50ml"
                else:
                    size_for_query = _normalize_size(sizes[0])

        brand_variants = _expand_brand(brand)
        conc_variants  = _expand_concentration(conc) if conc else []

        def join(*toks): return " ".join([t for t in toks if t and str(t).strip()])
        qs = []

        # A. 브랜드 + 제품명 + 농도 + 사이즈
        if brand_variants and name and conc_variants and size_for_query:
            for b in brand_variants:
                for c in conc_variants:
                    qs.append(join(b, name, c, size_for_query))

        # B. 브랜드 + 제품명 + 사이즈
        if brand_variants and name and size_for_query:
            for b in brand_variants:
                qs.append(join(b, name, size_for_query))

        # C. 브랜드 + 제품명 (백업)
        if brand_variants and name:
            for b in brand_variants:
                qs.append(join(b, name))

        # 중복 제거
        seen, deduped = set(), []
        for q in qs:
            if q not in seen:
                seen.add(q)
                deduped.append(q)

        results.append({
            "item_label": _make_display_name(meta, size_for_query),
            "queries": deduped[:6],
        })

    return results


# ========= LLM_parser_node (가격 검색 파트: vectorDB 아이템만 사용) =========
def LLM_parser_node(state: AgentState) -> AgentState:
    """실제 RAG 파이프라인을 실행하는 LLM_parser 노드 + 가격 검색(벡터DB 한정) 통합"""
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
        
        # 6단계: 가격 의도 감지
        price_keywords_ko = ['가격', '얼마', '가격대', '구매', '판매', '할인', '어디서 사', '어디서사', '배송비', '최저가']
        price_keywords_en = ['price', 'cost', 'cheapest', 'buy', 'purchase', 'discount']
        lower = user_query.lower()
        has_price_intent = any(k in user_query for k in price_keywords_ko) or any(k in lower for k in price_keywords_en)
        
        if has_price_intent:
            # 🔒 vectorDB에서 검색된 아이템만으로 가격 쿼리 생성
            item_query_bundles = build_item_queries_from_vectordb(
                search_results=search_results,
                facets=parsed_json,
                top_n_items=5
            )
            print("💰 가격 검색(벡터DB 한정) 대상:")
            for b in item_query_bundles:
                print(f" - {b['item_label']} :: {b['queries'][:3]}")

            price_sections = []
            for bundle in item_query_bundles:
                label = bundle["item_label"]
                queries = bundle["queries"]
                found_block = None

                for q in queries:
                    try:
                        res = price_tool.invoke({"user_query": q})
                        if res:  # 필요시 res 포맷에 맞춘 유효성 검사 추가
                            found_block = f"🔎 **{label}**\n(검색어: `{q}`)\n{res}"
                            break
                    except Exception as price_error:
                        print(f"❌ 가격 검색 오류({q}): {price_error}")
                        continue

                if found_block:
                    price_sections.append(found_block)

            if price_sections:
                final_response_with_price = f"""{final_response}

---

💰 **가격 정보 (vectorDB 추천만)**
{'\n\n'.join(price_sections)}"""
            else:
                final_response_with_price = f"""{final_response}

---

💰 **가격 정보 (vectorDB 추천만)**
🔍 벡터DB에서 추천된 제품명으로 검색했지만, 일치 결과를 찾지 못했어요.
원하시는 **제품명 + 농도 + 용량(예: 50ml)** 조합으로 다시 알려주세요."""
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
            ("system", """You are a perfume expert. Provide accurate and helpful information for users’ perfume-related questions.

You can cover topics such as:
- Perfume types and concentrations (EDT, EDP, Parfum, etc.)
- Fragrance notes and ingredients (top/middle/base) and their roles
- Brand characteristics and signature fragrances
- How to apply and store perfumes properly
- Tips for choosing perfumes by season and occasion
- Longevity (lasting power) and projection/sillage

Keep your tone friendly, explanations easy to understand, and include practical, actionable advice.
Please answer in Korean."""),
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
        system_prompt = """
You are a perfume recommendation explainer. The JSON below is the ML model's recommendation output; base your response solely on that information and craft a concise, friendly answer.

- Summarize the top 3 picks aligned with the user's intent, each with a key reason.
- If predicted scent attributes are present, show them in one line.
- Suggest about two similar alternatives and a next step (e.g., ask about season/time-of-day/longevity preferences).
- Do not exaggerate or invent any facts not present in the JSON.

Please answer in Korean.
"""
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
    

    # 기타 (노이즈성/실험용)
    "딥티끄 no5 추천해줘"
]
OUTPUT_FILE = "results.txt"

def run_tests():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for q in TEST_QUERIES:
            f.write("="*80 + "\n")
            f.write("Query: " + q + "\n")
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
                f.write("Router JSON: " + router_raw + "\n")
                f.write("Agent summary: " + agent_summary + "\n\n")
            except Exception as e:
                f.write(f"Error processing query: {e}\n\n")

def run_single_query(query: str):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"🔍 Query: {query}\n")
        f.write("-" * 50 + "\n")
        
        init: AgentState = {
            "messages": [HumanMessage(content=query)],
            "next": None,
            "router_json": None
        }
        
        try:
            out = app.invoke(init)
            ai_msgs = [m for m in out["messages"] if isinstance(m, AIMessage)]
            
            if len(ai_msgs) >= 2:
                f.write("🤖 Router Decision:\n")
                f.write(ai_msgs[-2].content + "\n")
                f.write("\n📝 Final Response:\n")
                f.write(ai_msgs[-1].content + "\n\n")
            elif len(ai_msgs) == 1:
                f.write("📝 Response:\n")
                f.write(ai_msgs[-1].content + "\n\n")
            else:
                f.write("❌ No response generated\n\n")
                
        except Exception as e:
            f.write(f"❌ Error: {e}\n\n")

if __name__ == "__main__":
    print("🔧 환경 변수 확인:")
    print(f"OPENAI_API_KEY: {'✅ 설정됨' if os.getenv('OPENAI_API_KEY') else '❌ 미설정'}")
    print(f"PINECONE_API_KEY: {'✅ 설정됨' if os.getenv('PINECONE_API_KEY') else '❌ 미설정'}")
    print(f"NAVER_CLIENT_ID: {'✅ 설정됨' if os.getenv('NAVER_CLIENT_ID') else '❌ 미설정'}")
    print(f"NAVER_CLIENT_SECRET: {'✅ 설정됨' if os.getenv('NAVER_CLIENT_SECRET') else '❌ 미설정'}")
    print()
    
    print("🚀 향수 추천 시스템 테스트 시작... 결과는 results.txt 파일에 저장됩니다.")
    print()
    
    run_tests()