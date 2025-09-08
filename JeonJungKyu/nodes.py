import json
for m in reversed(state.get('messages', [])):
if isinstance(m, HumanMessage):
user_query = m.content; break
user_query = user_query or '(empty)'
try:
price = price_tool.invoke({"user_query": user_query})
return {"messages": state.get('messages', []) + [AIMessage(content=f"💰 **가격 정보**\n\n{price}")], "next": None, "router_json": state.get('router_json')}
except Exception as e:
return {"messages": state.get('messages', []) + [AIMessage(content=f"❌ 가격 조회 오류: {e}")], "next": None, "router_json": state.get('router_json')}
return node




def faq_agent_node_factory(faq_tool):
def node(state):
user_query = None
for m in reversed(state.get('messages', [])):
if isinstance(m, HumanMessage):
user_query = m.content; break
user_query = user_query or '(empty)'
try:
ans = faq_tool.invoke({"question": user_query})
return {"messages": state.get('messages', []) + [AIMessage(content=f"📚 **향수 지식**\n\n{ans}")], "next": None, "router_json": state.get('router_json')}
except Exception as e:
return {"messages": state.get('messages', []) + [AIMessage(content=f"❌ 지식 검색 오류: {e}")], "next": None, "router_json": state.get('router_json')}
return node




def ml_agent_node_factory(reco_tool):
def node(state):
user_query = None
for m in reversed(state.get('messages', [])):
if isinstance(m, HumanMessage):
user_query = m.content; break
user_query = user_query or '(empty)'
try:
res = reco_tool.invoke({"user_text": user_query})
if isinstance(res, dict) and 'recommendations' in res:
recs = res['recommendations']; labels = res.get('predicted_labels', [])
lines = ["🎯 **향수 추천 결과**\n", f"📊 예측된 향 특성: {', '.join(labels)}\n"]
for r in recs:
lines.append(f"🏆 **{r['rank']}위** - {r['brand']} {r['name']}\n 🌸 향료: {r['fragrances']}")
out = "\n".join(lines)
else:
out = f"🎯 **향수 추천**\n\n{str(res)}"
return {"messages": state.get('messages', []) + [AIMessage(content=out)], "next": None, "router_json": state.get('router_json')}
except Exception as e:
return {"messages": state.get('messages', []) + [AIMessage(content=f"❌ ML 추천 오류: {e}")], "next": None, "router_json": state.get('router_json')}
return node




def human_fallback_node_factory():
def node(state):
user_query = None
for m in reversed(state.get('messages', [])):
if isinstance(m, HumanMessage):
user_query = m.content; break
user_query = user_query or '(empty)'
msg = (
f"❓ '{user_query}' 더 명확한 설명이 필요합니다.\n"
f"👉 질문을 구체적으로 다시 작성해 주세요.\n"
f"💡 또는 향수에 관한 멋진 질문을 해보시는 건 어떨까요?"
)
return {"messages": state.get('messages', []) + [AIMessage(content=msg)], "next": None, "router_json": state.get('router_json')}
return node