# main.py
import os
from dotenv import load_dotenv
from typing import TypedDict, Optional, Annotated, Sequence
import operator

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# 시각화를 위한 추가 import
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # GUI 없이 사용
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️ matplotlib 없음. 시각화 기능 비활성화")

from function import price_tool, human_fallback

# --- 0) ENV ---
load_dotenv()

# --- 1) State 정의 ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: Optional[str]

# --- 2) LLM ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- 3) Supervisor ---
members = ["price_agent", "consultation_agent", "human_fallback"]

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a supervisor managing a perfume specialist team.

Your team members:
- price_agent: Handles perfume price/cost inquiries (has access to Naver Shopping API)
- consultation_agent: Handles general perfume advice and recommendations  
- human_fallback: Handles non-perfume topics or unclear questions

Routing Rules:
- If query is about perfume price/cost (가격, 최저가, 얼마, price, cost, 구매, 판매), choose "price_agent"
- If query is perfume-related advice/recommendation (추천, 향수, 냄새, 향, fragrance), choose "consultation_agent"  
- If query is NOT about perfumes or is unclear/vague, choose "human_fallback"

Respond with ONLY the agent name."""),
    ("placeholder", "{messages}"),
])

def supervisor_node(state: AgentState) -> dict:
    """Supervisor 노드"""
    chain = supervisor_prompt | llm
    result = chain.invoke(state)
    
    next_agent = result.content.strip()
    if next_agent not in members:
        next_agent = "human_fallback"  # 기본값
    
    return {"next": next_agent}

# --- 4) Price Agent (도구 포함) ---
price_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a perfume price specialist assistant.
    
When users ask about perfume prices:
1. Use the price_tool to search for current prices
2. Always respond in Korean
3. Format results nicely with emojis and clear information
4. Be helpful and friendly
    
If you can't find price information, politely explain and suggest alternative searches."""),
    ("placeholder", "{messages}"),
])

price_agent = create_react_agent(
    llm, 
    [price_tool],
    prompt=price_prompt
)

# --- 5) Consultation Agent (일반 상담) ---
consultation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledgeable and friendly perfume consultant.
    
Your expertise includes:
- Perfume recommendations based on preferences, occasions, seasons
- Fragrance families and notes explanation
- Perfume wearing tips and application advice
- Brand and fragrance history knowledge

Always respond in Korean with:
- Warmth and professionalism
- Helpful and detailed advice
- Relevant examples and suggestions
- Encouraging tone

If questions are too vague, politely ask for more specific information to provide better recommendations."""),
    ("placeholder", "{messages}"),
])

consultation_agent = create_react_agent(
    llm,
    [],  # 도구 없음
    prompt=consultation_prompt
)

# --- 6) Human Fallback Node ---
def human_fallback_node(state: AgentState) -> dict:
    """향수와 관련 없거나 불명확한 질문 처리"""
    # 마지막 메시지에서 사용자 입력 추출
    messages = state.get("messages", [])
    user_input = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
    
    # human_fallback 함수 호출 (state dict 형태로 전달)
    fallback_result = human_fallback({"input": user_input})
    
    # 시스템 메시지로 응답 생성
    response_msg = HumanMessage(content=fallback_result)
    
    return {"messages": [response_msg]}

# --- 7) 에이전트 호출 래퍼 ---
def price_agent_node(state: AgentState) -> dict:
    """Price agent 호출"""
    result = price_agent.invoke(state)
    return {"messages": result["messages"]}

def consultation_agent_node(state: AgentState) -> dict:
    """Consultation agent 호출"""
    result = consultation_agent.invoke(state)
    return {"messages": result["messages"]}

# --- 8) Graph 구성 ---
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("price_agent", price_agent_node)
workflow.add_node("consultation_agent", consultation_agent_node)
workflow.add_node("human_fallback", human_fallback_node)

# 조건부 엣지: supervisor → agents
workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {
        "price_agent": "price_agent",
        "consultation_agent": "consultation_agent",
        "human_fallback": "human_fallback",
    }
)

# 각 에이전트에서 END로
workflow.add_edge("price_agent", END)
workflow.add_edge("consultation_agent", END)
workflow.add_edge("human_fallback", END)

# 시작점
workflow.set_entry_point("supervisor")

# 컴파일
app = workflow.compile()

# --- 9) 시각화 함수 ---
def visualize_graph():
    """그래프 구조 시각화"""
    if not VISUALIZATION_AVAILABLE:
        print("❌ matplotlib이 설치되지 않아 시각화를 사용할 수 없습니다.")
        print("설치: pip install matplotlib")
        return
    
    try:
        # LangGraph 내장 시각화
        img_data = app.get_graph().draw_mermaid_png()
        
        # 파일로 저장
        with open("perfume_bot_graph.png", "wb") as f:
            f.write(img_data)
        print("✅ 그래프가 'perfume_bot_graph.png'로 저장되었습니다!")
        
    except Exception as e:
        print(f"❌ 시각화 오류: {e}")
        print("대신 텍스트로 그래프 구조를 출력합니다:")
        print_graph_structure()

def print_graph_structure():
    """텍스트로 그래프 구조 출력"""
    print("""
    🌟 향수 봇 그래프 구조:
    
    [사용자 입력] 
           ↓
    📋 Supervisor 
           ↓
    ┌──────┴──────┬──────────────┐
    ↓             ↓              ↓
💰 Price        🌸 Consultation  ❓ Human
  Agent           Agent          Fallback
(price_tool)    (상담 전문)      (기타/모호)
    ↓             ↓              ↓
   END           END            END
    """)

def show_graph_info():
    """그래프 정보 출력"""
    print("📊 그래프 정보:")
    print(f"노드 수: {len(app.get_graph().nodes)}")
    print(f"엣지 수: {len(app.get_graph().edges)}")
    print("노드 목록:", list(app.get_graph().nodes.keys()))
    print_graph_structure()

# --- 9) 편의 함수 ---
def ask_perfume_bot(question: str) -> str:
    """간단한 질문-답변 인터페이스"""
    try:
        result = app.invoke({
            "messages": [HumanMessage(content=question)]
        })
        
        # 마지막 AI 메시지 추출
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content and msg.__class__.__name__ != 'HumanMessage':
                return msg.content
        
        return "응답을 생성할 수 없습니다."
    
    except Exception as e:
        return f"❌ 오류 발생: {e}"

# --- 10) 테스트 실행 ---
def run_interactive_test():
    """대화형 테스트 모드"""
    print("🌸 향수 전문가 AI 챗봇 (종료: 'quit' 입력)")
    print("=" * 50)
    
    while True:
        user_input = input("\n💬 질문: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료', 'q']:
            print("👋 안녕히 가세요!")
            break
            
        if not user_input:
            continue
            
        print("🤖 생각 중...")
        answer = ask_perfume_bot(user_input)
        print(f"\n✨ 답변:\n{answer}")
        print("-" * 50)

def run_batch_test():
    """미리 정의된 테스트 케이스 실행"""
    print("=== 향수 전문가 배치 테스트 ===")
    
    test_queries = [
        # 가격 관련 (price_agent로 라우팅)
        "샤넬 넘버5 가격 알려줘",
        "디올 소바쥬 최저가 찾아줘", 
        "톰포드 블랙 오키드 얼마야?",
        
        # 상담 관련 (consultation_agent로 라우팅)
        "여름에 어울리는 시트러스 향수 추천",
        "로맨틱한 향수 뭐가 좋을까?",
        "20대 여성에게 어울리는 향수",
        
        # 모호하거나 향수 무관 (human_fallback으로 라우팅)
        "엄마가 쓰던 향수 알려줘",  # 너무 모호함
        "오늘 날씨 어때?",  # 향수 무관
        "안녕하세요"  # 불명확
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] 📝 질문: {query}")
        answer = ask_perfume_bot(query)
        print(f"✅ 답변: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    print("🌸 향수 전문가 AI 봇")
    print("=" * 50)
    
    print("선택하세요:")
    print("1. 대화형 테스트")
    print("2. 배치 테스트") 
    print("3. 그래프 시각화")
    print("4. 그래프 정보 보기")
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        run_interactive_test()
    elif choice == "2":
        run_batch_test()
    elif choice == "3":
        visualize_graph()
    elif choice == "4":
        show_graph_info()
    else:
        print("잘못된 선택입니다. 배치 테스트를 실행합니다.")
        run_batch_test()