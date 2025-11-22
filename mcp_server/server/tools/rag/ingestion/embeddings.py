from langchain_ollama import OllamaEmbeddings

from mcp_server.utils.logger import get_logger
from mcp_server.utils.custom_exception import CustomException
from mcp_server.config.constants import OLLAMA_BASE_URL,EMBED_MODEL

logger = get_logger(__name__)

_embedding_model = None

def get_embedding_model():

    global _embedding_model

    if _embedding_model:
        return _embedding_model

    try:
        logger.info("Initializing embedding model for the first time...")
        _embedding_model = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
        logger.info("Embedding model loaded successfully.")
        return _embedding_model
    
    except Exception as e:
        error_message = CustomException("Error occurred while loading embedding model", e)
        logger.error(str(error_message))
        raise error_message