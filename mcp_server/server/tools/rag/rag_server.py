import chromadb

from fastmcp import FastMCP
from typing import List, Optional, Literal
from pathlib import Path
from mcp_server.server.tools.rag.ingestion.pdf_loader import PDFLoader
from mcp_server.server.tools.rag.ingestion.chunking import chunk_documents
from mcp_server.server.tools.rag.ingestion.vector_store import get_or_create_vector_store
from mcp_server.utils.logger import get_logger
from mcp_server.config.constants import VECTOR_DB_PATH, CHROMA_COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K

logger = get_logger(__name__)

mcp = FastMCP(
    "RAG MCP",
    stateless_http=True)

@mcp.tool()
def ingest_documents(
    source: str,
    source_type: Literal["auto", "file", "directory", "url"] = "auto",
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    update_mode: Literal["skip", "upsert"] = "skip",
    enable_cache: bool = True
) -> dict:
    """
    Ingest PDF documents into the vector store from various sources.
    
    Args:
        source: Path to file/directory or URL to PDF document(s)
        source_type: Type of source - "auto" (default), "file", "directory", or "url"
        chunk_size: Size of text chunks for splitting (default: 1000)
        chunk_overlap: Overlap between chunks (default: 200)
        update_mode: How to handle existing documents - "skip" (default) or "upsert"
        enable_cache: Enable caching for URL downloads (default: True)
    
    Returns:
        Dictionary with ingestion statistics including number of documents processed
    """
    try:
        logger.info(f"Starting document ingestion from: {source}")
        
        pdf_loader = PDFLoader(enable_cache=enable_cache)
        documents = pdf_loader.load(source=source, source_type=source_type)
        
        if not documents:
            return {
                "success": False,
                "error": "No documents were loaded",
                "documents_loaded": 0
            }
        
        logger.info(f"Loaded {len(documents)} pages from PDF(s)")
        
        text_chunks = chunk_documents(
            documents=documents,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        logger.info(f"Created {len(text_chunks)} text chunks")
        
        vector_store = get_or_create_vector_store(
            text_chunks=text_chunks,
            update_mode=update_mode
        )
        
        collection = vector_store._collection
        total_docs = collection.count()
        
        return {
            "success": True,
            "source": source,
            "source_type": source_type,
            "pages_loaded": len(documents),
            "chunks_created": len(text_chunks),
            "total_documents_in_store": total_docs,
            "update_mode": update_mode,
            "message": f"Successfully ingested {len(documents)} pages into {len(text_chunks)} chunks"
        }
        
    except Exception as e:
        logger.exception(f"Failed to ingest documents from {source}")
        return {
            "success": False,
            "error": str(e),
            "source": source
        }


@mcp.tool()
def retrieve_documents(
    query: str,
    top_k: int = TOP_K
) -> dict:
    """
    Retrieve relevant documents from the vector store based on a query.
    
    Args:
        query: Search query text
        top_k: Number of top results to return (default: 5)
    
    Returns:
        Dictionary containing relevant documents with their content, metadata, and scores
    """
    try:
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty"
            }
        
        logger.info(f"Retrieving documents for query: {query}")
        
        # Load vector store
        vector_store = get_or_create_vector_store()
        
        results = vector_store.similarity_search_with_score(
            query=query,
            k=top_k
        )
        
        # Format results
        retrieved_docs = []
        for i, (doc, score) in enumerate(results, 1):
            retrieved_docs.append({
                "rank": i,
                "content": doc.page_content,
                "score": float(score),
                "metadata": {
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", "unknown")
                }
            })
        
        return {
            "success": True,
            "query": query,
            "total_results": len(retrieved_docs),
            "top_k": top_k,
            "documents": retrieved_docs
        }
        
    except Exception as e:
        logger.exception(f"Failed to retrieve documents for query: {query}")
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@mcp.tool()
def get_vector_store_info(
    query: Optional[str] = None
) -> dict:
    """
    Get detailed information about the vector store including statistics and configuration.

    The 'query' parameter is optional and ignored. It exists so that
    LLMs can safely call this tool even if they pass query="...".
    """
    try:
        logger.info("Retrieving vector store information")
        
        db_path = Path(VECTOR_DB_PATH)
        exists = db_path.exists()
        
        info = {
            "exists": exists,
            "collection_name": CHROMA_COLLECTION_NAME,
            "storage_path": VECTOR_DB_PATH,
        }
        
        if exists:
            try:
                # Load vector store to get stats
                vector_store = get_or_create_vector_store()
                collection = vector_store._collection
                
                doc_count = collection.count()
                
                info.update({
                    "document_count": doc_count,
                    "status": "active"
                })
                
                if doc_count > 0:
                    sample_docs = collection.get(limit=1, include=["metadatas"])
                    if sample_docs:
                        metadatas = sample_docs.get("metadatas")
                        if metadatas and len(metadatas) > 0:
                            info["sample_metadata"] = metadatas[0]
                
            except Exception as e:
                info.update({
                    "status": "error",
                    "error": str(e)
                })
        else:
            info["status"] = "not_initialized"
        
        # Get cache information
        pdf_loader = PDFLoader()
        cache_info = pdf_loader.get_cache_info()
        info["cache"] = cache_info
        
        return {
            "success": True,
            "vector_store": info
        }
        
    except Exception as e:
        logger.exception("Failed to retrieve vector store information")
        return {
            "success": False,
            "error": str(e)
        }



@mcp.tool()
def clear_vector_store(
    confirm: bool = False
) -> dict:
    """
    Clear the vector store by removing the collection via ChromaDB API.
    
    WARNING: This operation is irreversible and will delete all stored documents.
    
    Args:
        confirm: Must be set to True to confirm deletion (safety measure)
    
    Returns:
        Dictionary with deletion status and details
    """
    try:
        if not confirm:
            return {
                "success": False,
                "error": "Deletion not confirmed. Set confirm=True to proceed.",
                "warning": "This operation will permanently delete all documents in the vector store."
            }
        
        logger.warning("Clearning vector store - this operation is irreversible")
        
        db_path = Path(VECTOR_DB_PATH)
        deleted_items = []
        
        if db_path.exists():
            try:
                # Use ChromaDB API to delete the collection 
                client = chromadb.PersistentClient(path=str(db_path))
                
                try:
                    collection = client.get_collection(CHROMA_COLLECTION_NAME)
                    doc_count = collection.count()
                    deleted_items.append(f"vector_store ({doc_count} documents)")
                except Exception:
                    doc_count = 0
                    deleted_items.append("vector_store")
                
                client.delete_collection(CHROMA_COLLECTION_NAME)
                logger.info(f"Deleted collection '{CHROMA_COLLECTION_NAME}'")     
                # Clean up client reference
                del client
                
                return {
                    "success": True,
                    "deleted": deleted_items,
                    "message": f"Successfully deleted vector store with {doc_count} documents"
                }
                
            except Exception as e:
                logger.error(f"Failed to delete vector store: {e}")
                return {
                    "success": False,
                    "error": f"Failed to delete vector store: {str(e)}"
                }
        else:
            logger.info("Vector store does not exist, nothing to delete")
            return {
                "success": True,
                "deleted": [],
                "message": "Vector store does not exist"
            }
        
    except Exception as e:
        logger.exception("Failed to delete vector store")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=3000)