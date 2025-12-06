from langchain_core.runnables import RunnableConfig

config: RunnableConfig = {
    "configurable": {"thread_id": "1"}
}

MODEL_NAME = "openai/gpt-oss-20b"
TEMPERATURE = 0.0