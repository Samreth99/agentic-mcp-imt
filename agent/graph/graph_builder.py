from agent.graph.nodes.generate import Generator_Agent
from agent.graph.state.state import State
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver


memory=MemorySaver()

def build_graph(tools, 
        system_prompt, 
        model_name,
        temperature):

    agent = Generator_Agent(tools=tools, 
        system_prompt=system_prompt, 
        model_name=model_name,
        temperature = temperature)
    
    builder = StateGraph(State)

    builder.add_node("call_model", agent)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,     
    )
    builder.add_edge("tools", "call_model")

    return builder.compile(memory)