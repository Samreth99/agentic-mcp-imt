
import traceback
from typing import Any
from graph.graph_builder import build_graph
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AIMessage
from agent.graph.state.state import State
from langchain_core.messages import AnyMessage
from agent.config.prompts import AGENT_SYSTEM_PROMPT
from agent.config.constants import MODEL_NAME, TEMPERATURE
from agent.config.constants import config

class Agent_Client:
    def __init__(self) -> None:
        self.system_prompt = AGENT_SYSTEM_PROMPT
        self.model_name =  MODEL_NAME
        self.temperature = TEMPERATURE
        self.client: MultiServerMCPClient | None = None
        self.agent: Any = None
        self.is_initialized = False

    async def initialize(self) -> None:
        try:
            self.client = MultiServerMCPClient(
                {
                    "rag_server": {
                        "url": "http://127.0.0.1:3000/mcp/",
                        "transport": "streamable_http"
                    },
                }
            )
            tools = await self.client.get_tools()
            self.agent = build_graph(tools, 
                                    self.system_prompt, 
                                    self.model_name,
                                    self.temperature)
            self.is_initialized = True
        except Exception:
            traceback.print_exc()
            raise

    async def ask(self, messages: list[AnyMessage]) -> str:
        try:
            if not self.is_initialized:
                await self.initialize()

            state: State = {"messages": messages}
            result = await self.agent.ainvoke(state, config=config)

            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    content = msg.content
                    if isinstance(content, str):
                        return content
                    return str(content)

            return "No valid AI response."
        except Exception as e:
            traceback.print_exc()
            return f"Error: {e}"

    async def close(self):
        self.client = None
        self.agent = None
        self.is_initialized = False