from typing import TypedDict, Sequence, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from app.config import MODEL_NAME, GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools import (
    get_stock_price, get_company_overview, search_finance_docs,
    calculate_sip, calculate_emi, assess_risk_profile, generate_budget
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agent: str

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)

# Agent Definitions
research_tools = [get_stock_price, get_company_overview]
calculator_tools = [calculate_sip, calculate_emi, assess_risk_profile, generate_budget]
rag_tools = [search_finance_docs]

research_agent = create_react_agent(llm, tools=research_tools)
calculator_agent = create_react_agent(llm, tools=calculator_tools)
rag_agent = create_react_agent(llm, tools=rag_tools)

# Node Wrappers
async def research_node(state: AgentState):
    result = await research_agent.ainvoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

async def calculator_node(state: AgentState):
    result = await calculator_agent.ainvoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

async def rag_node(state: AgentState):
    result = await rag_agent.ainvoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

async def router_node(state: AgentState):
    # Simple semantic router using LLM
    last_message = state["messages"][-1].content.lower()
    if "calculate" in last_message or "emi" in last_message or "sip" in last_message or "budget" in last_message or "risk" in last_message:
        return {"next_agent": "Calculator"}
    elif "report" in last_message or "document" in last_message or "annual" in last_message:
        return {"next_agent": "RAG"}
    else:
        return {"next_agent": "Research"}

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("Router", router_node)
workflow.add_node("Research", research_node)
workflow.add_node("Calculator", calculator_node)
workflow.add_node("RAG", rag_node)

workflow.set_entry_point("Router")

workflow.add_conditional_edges(
    "Router",
    lambda x: x["next_agent"],
    {
        "Research": "Research",
        "Calculator": "Calculator",
        "RAG": "RAG"
    }
)

workflow.add_edge("Research", END)
workflow.add_edge("Calculator", END)
workflow.add_edge("RAG", END)

app_graph = workflow.compile()
