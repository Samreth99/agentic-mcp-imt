from langchain_community.vectorstores import Chroma
from mcp_server.server.tools.rag.ingestion.embeddings import get_embedding_model
from mcp_server.utils.logger import get_logger
from mcp_server.utils.custom_exception import CustomException
from mcp_server.config.constants import VECTOR_DB_PATH, CHROMA_COLLECTION_NAME

logger = get_logger(__name__)

def get_vector_store(text_chunks=None):
    """
    Loads an existing ChromaDB vector store or creates a new one.

    Args:
        text_chunks: A list of text chunks to use for creating/updating the store.

    Returns:
        A Chroma vector store instance.
    """
    try:
        embedding_model = get_embedding_model()

        # Case 1: Create or update the store with new documents.
        if text_chunks:
            logger.info(f"Creating or updating Chroma vector store at '{VECTOR_DB_PATH}'...")
            db = Chroma.from_documents(
                documents=text_chunks,
                embedding=embedding_model,
                collection_name=CHROMA_COLLECTION_NAME,
                persist_directory=VECTOR_DB_PATH
            )
            logger.info(f"Chroma vector store created/updated and saved successfully.")
            return db

        # Case 2: Load the existing store without adding new documents.
        else:
            logger.info(f"Loading existing Chroma vector store from '{VECTOR_DB_PATH}'...")
            db = Chroma(
                persist_directory=VECTOR_DB_PATH,
                embedding_function=embedding_model,
                collection_name=CHROMA_COLLECTION_NAME
            )
            logger.info("Chroma vector store loaded successfully.")
            return db

    except Exception as e:
        if "Could not find a Chroma collection" in str(e) or "does not exist" in str(e):
             raise CustomException(f"Vector store not found at '{VECTOR_DB_PATH}'. Provide text_chunks to create it.", e) from e
        
        error_message = CustomException("Failed to get or create Chroma vector store", e)
        logger.error(str(error_message))
        raise error_message from e
