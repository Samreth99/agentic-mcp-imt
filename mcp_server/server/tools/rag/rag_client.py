import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    url = "http://127.0.0.1:3000/mcp/"
    async with streamablehttp_client(url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            print("Before initialize:", get_session_id())

            await session.initialize()

            sid = get_session_id()
            print("Session ID after initialize:", sid)

            # result = await session.call_tool("delete_vector_store", {"confirm": True})
            # result = await session.call_tool("ingest_documents", {"source": "D:\\IMT\\Lesson\\S9\\(2IA-IASD 9.6) - Deep Learning\\agentic_mcp\\mcp_server\\server\\tools\\rag\\data"})
            # result = await session.call_tool("get_vector_store_info", {})
            result = await session.call_tool("retrieve_documents", {"query": "Who is the responsable of this Module Mathematic for Machine Learning?"})
            print("Server result:", result)


if __name__ == "__main__":
    asyncio.run(main())