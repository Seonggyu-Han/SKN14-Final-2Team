from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, List, Optional, Dict, Any


from nodes import (
supervisor_node_factory, llm_parser_node_factory, price_agent_node_factory,
faq_agent_node_factory, ml_agent_node_factory, human_fallback_node_factory,
)
from tools import price_tool_factory, faq_tool_factory, recommender_tool_factory


class AgentState(TypedDict, total=False):
messages: List[BaseMessage]
next: Optional[str]
router_json: Optional[Dict[str, Any]]




def build_graph(ctx):
g = StateGraph(AgentState)


price_tool = price_tool_factory(ctx)
faq_tool = faq_tool_factory()
rec_tool = recommender_tool_factory()


g.add_node("supervisor", supervisor_node_factory(ctx))
g.add_node("LLM_parser", llm_parser_node_factory(ctx, price_tool))
g.add_node("FAQ_agent", faq_agent_node_factory(faq_tool))
g.add_node("human_fallback", human_fallback_node_factory())
g.add_node("price_agent", price_agent_node_factory(price_tool))
g.add_node("ML_agent", ml_agent_node_factory(rec_tool))


g.set_entry_point("supervisor")


def router_edge(state: AgentState) -> str:
return state.get("next") or "human_fallback"


g.add_conditional_edges("supervisor", router_edge, {
"LLM_parser": "LLM_parser",
"FAQ_agent": "FAQ_agent",
"human_fallback": "human_fallback",
"price_agent": "price_agent",
"ML_agent": "ML_agent",
})


for n in ["LLM_parser","FAQ_agent","human_fallback","price_agent","ML_agent"]:
g.add_edge(n, END)


return g.compile()