from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from app.guardrails import check_and_redact
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="enterprise-chat",
    base_url="http://localhost:4000/v1",
    api_key="sk-local-gateway",
    temperature=0,
)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    is_safe: bool
    flags: list[str]

# Option A: Routed through LiteLLM Proxy with automatic failover (Primary: Groq Qwen, Fallback: Gemini Flash)
# llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)  # Direct Groq (bypassing proxy)

def input_guard_node(state: AgentState):
    last_msg = state["messages"][-1].content
    is_safe, clean_text, flags = check_and_redact(last_msg)
    if not is_safe:
        return {
            "is_safe": False,
            "flags": flags,
            "messages": [("assistant", "Request blocked by security policy.")],
        }
    state["messages"][-1].content = clean_text
    return {"is_safe": True, "flags": flags}

def llm_node(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def route_after_guard(state: AgentState):
    return "llm" if state["is_safe"] else END

builder = StateGraph(AgentState)
builder.add_node("guard", input_guard_node)
builder.add_node("llm", llm_node)
builder.add_edge(START, "guard")
builder.add_conditional_edges("guard", route_after_guard, {"llm": "llm", END: END})
builder.add_edge("llm", END)

agent_graph = builder.compile()