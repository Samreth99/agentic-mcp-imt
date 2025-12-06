import os
import json
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from agent.config.setting import settings
from agent.config.constants import config
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

# current_dir = os.path.dirname(os.path.abspath(__file__))
# mcp_config_path = os.path.join(current_dir, "mcp.json")
# mcp_json = json.load(open(mcp_config_path, 'r'))

# memory = MemorySaver()

async def main():

    client = MultiServerMCPClient(
        {
            "rag_server": {
                "url": "http://127.0.0.1:3000/mcp/",
                "transport": "streamable_http"
            },
        }
    )

    # model = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")
    model = ChatGroq(model = "openai/gpt-oss-20b")

    tools = await client.get_tools()

    agent = create_agent(model, tools)

    
    agent_response = await agent.ainvoke({"messages": [{"role": "user", "content": "Who is responsible for Mathematic for Machine Learning Module? use rag tool"}]})
    response = agent_response['messages'][-1].content
    print(f"\nResponse: {response}")

if __name__ == "__main__":
    asyncio.run(main())
    # print(mcp_json)