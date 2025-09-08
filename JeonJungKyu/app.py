import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone
from context import AppContext
from config import OPENAI_MODEL, EMBED_MODEL, PINECONE_API_KEY, PINECONE_INDEX, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from graph import build_graph
from langchain_core.messages import HumanMessage, AIMessage


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
]




def create_context() -> AppContext:
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
pc = Pinecone(api_key=PINECONE_API_KEY) if PINECONE_API_KEY else None
index = pc.Index(PINECONE_INDEX) if pc and PINECONE_INDEX else None
return AppContext(
llm=llm,
embeddings=embeddings,
pc=pc,
index=index,
naver_client_id=NAVER_CLIENT_ID,
naver_client_secret=NAVER_CLIENT_SECRET,
)




def run_tests(app):
for q in TEST_QUERIES:
print("="*80)
print("Query:", q)
init = {"messages": [HumanMessage(content=q)], "next": None, "router_json": None}
out = app.invoke(init)
ai_msgs = [m for m in out["messages"] if isinstance(m, AIMessage)]
router_raw = ai_msgs[-2].content if len(ai_msgs) >= 2 else "(no router output)"
agent_summary = ai_msgs[-1].content if ai_msgs else "(no agent output)"
print("Router JSON:", router_raw)
print("Agent summary:", agent_summary)




def run_single_query(app, query: str):
print(f"🔍 Query: {query}")
print("-" * 50)
init = {"messages": [HumanMessage(content=query)], "next": None, "router_json": None}
out = app.invoke(init)
ai_msgs = [m for m in out["messages"] if isinstance(m, AIMessage)]
if len(ai_msgs) >= 2:
print("🤖 Router Decision:\n", ai_msgs[-2].content)
print("\n📝 Final Response:\n", ai_msgs[-1].content)
elif len(ai_msgs) == 1:
print("📝 Response:\n", ai_msgs[-1].content)
else:
print("🚀 Ready. Use run_tests(app) or run_single_query(app, '...')")