from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from mcp_server.utils.logger import get_logger
from mcp_server.config.constants import CHUNK_SIZE, CHUNK_OVERLAP

logger = get_logger(__name__)


def chunk_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.
    
    Args:
        documents: List of documents to chunk
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of overlapping characters between chunks
        
    Returns:
        List of chunked documents
    """
    if not documents:
        error_msg = "Cannot chunk empty document list"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if chunk_size <= 0 or chunk_overlap < 0:
        error_msg = f"Invalid parameters: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if chunk_overlap >= chunk_size:
        logger.warning(f"chunk_overlap ({chunk_overlap}) >= chunk_size ({chunk_size}), setting overlap to {chunk_size // 2}")
        chunk_overlap = chunk_size // 2
    
    logger.info(f"Splitting {len(documents)} documents into chunks (size={chunk_size}, overlap={chunk_overlap})")
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[" "]
        )
        
        text_chunks = text_splitter.split_documents(documents)
        
        # Add chunk index to metadata for unique ID generation
        for i, chunk in enumerate(text_chunks):
            chunk.metadata["chunk_index"] = i
            
        logger.info(f"Successfully generated {len(text_chunks)} text chunks from {len(documents)} documents")
        return text_chunks
        
    except Exception as e:
        logger.exception(f"Failed to chunk documents: {e}")
        raise  