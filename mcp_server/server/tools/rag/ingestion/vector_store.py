import hashlib
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from mcp_server.server.tools.rag.ingestion.embeddings import get_embedding_model
from mcp_server.utils.logger import get_logger
from mcp_server.utils.custom_exception import CustomException
from mcp_server.config.constants import VECTOR_DB_PATH, CHROMA_COLLECTION_NAME
from pathlib import Path

logger = get_logger(__name__)

def generate_document_id(doc: Document) -> str:
    """
    Generate a unique ID based on stable document attributes.
    Uses source file, page number, and chunk index for consistency.
    """
    source = doc.metadata.get('source', '')
    page = doc.metadata.get('page', 0)
    chunk_index = doc.metadata.get('chunk_index', 0)
    source_name = Path(source).name if source else 'unknown'

    stable_id = f"{source_name}|page:{page}|chunk:{chunk_index}"
    return hashlib.sha256(stable_id.encode()).hexdigest()


def get_existing_doc_ids(vector_store: Chroma) -> set:
    """
    Retrieve all existing document IDs from the vector store.
    """
    try:
        collection = vector_store._collection
        all_ids = collection.get(include=[])['ids']
        
        existing_ids = set(all_ids)
        
        logger.info(f"Found {len(existing_ids)} existing documents in vector store")
        return existing_ids
    
    except Exception as e:
        logger.warning(f"Could not retrieve existing IDs: {e}")
        return set()


def get_or_create_vector_store(
    text_chunks: Optional[List[Document]] = None,
    update_mode: str = "skip"  # "skip" or "upsert"
):
    """
    Loads an existing ChromaDB vector store or creates a new one.
    
    If `text_chunks` are provided, they can be added to the store using
    different strategies defined by `update_mode`.

    Args:
        text_chunks: List of Document objects to add/update.
        update_mode: How to handle existing documents.
            - "skip": Skip documents that already exist (default).
            - "upsert": Add new documents and update existing ones.
    
    Returns:
        A Chroma vector store instance.
    """
    try:
        embedding_model = get_embedding_model()

        # Case 1: Load existing store without adding documents
        if text_chunks is None:
            logger.info(f"Loading existing Chroma vector store from '{VECTOR_DB_PATH}'...")
            db = Chroma(
                persist_directory=VECTOR_DB_PATH,
                embedding_function=embedding_model,
                collection_name=CHROMA_COLLECTION_NAME
            )
            logger.info("Chroma vector store loaded successfully.")
            return db

        # Case 2: Create new store or update existing one
        logger.info(f"Processing {len(text_chunks)} documents...")
        
        # Assign IDs to all documents
        doc_ids = [generate_document_id(doc) for doc in text_chunks]
        
        # Add ID to metadata for reference
        for doc, doc_id in zip(text_chunks, doc_ids):
            doc.metadata['doc_id'] = doc_id

        try:
            db = Chroma(
                persist_directory=VECTOR_DB_PATH,
                embedding_function=embedding_model,
                collection_name=CHROMA_COLLECTION_NAME
            )
            existing_ids = get_existing_doc_ids(db)
            logger.info(f"Loaded existing vector store with {len(existing_ids)} documents")
            
        except Exception:
            logger.info("No existing vector store found, creating new one...")
            db = Chroma.from_documents(
                documents=text_chunks,
                embedding=embedding_model,
                collection_name=CHROMA_COLLECTION_NAME,
                persist_directory=VECTOR_DB_PATH,
                ids=doc_ids
            )
            logger.info(f"Created new vector store with {len(text_chunks)} documents")
            return db

        if update_mode == "upsert":
            # Separate documents for adding and updating
            docs_to_add, ids_to_add = [], []
            docs_to_update, ids_to_update = [], []

            for doc, doc_id in zip(text_chunks, doc_ids):
                if doc_id in existing_ids:
                    docs_to_update.append(doc)
                    ids_to_update.append(doc_id)
                else:
                    docs_to_add.append(doc)
                    ids_to_add.append(doc_id)

            if docs_to_update:
                db.update_documents(ids=ids_to_update, documents=docs_to_update)
                logger.info(f"Updated {len(docs_to_update)} existing documents (mode: upsert)")

            if docs_to_add:
                db.add_documents(documents=docs_to_add, ids=ids_to_add)
                logger.info(f"Added {len(docs_to_add)} new documents (mode: upsert)")

            if not docs_to_update and not docs_to_add:
                logger.info("No documents to add or update.")
            
        elif update_mode == "skip":
            new_docs = []
            new_ids = []
            skipped_count = 0
            
            for doc, doc_id in zip(text_chunks, doc_ids):
                if doc_id not in existing_ids:
                    new_docs.append(doc)
                    new_ids.append(doc_id)
                else:
                    skipped_count += 1
            
            if new_docs:
                db.add_documents(documents=new_docs, ids=new_ids)
                logger.info(f"Added {len(new_docs)} new documents, skipped {skipped_count} existing (mode: skip)")
            else:
                logger.info(f"No new documents to add, all {skipped_count} already exist.")
        
        else:
            raise ValueError(f"Invalid update_mode: '{update_mode}'. Supported modes are 'skip' and 'upsert'.")

        return db

    except Exception as e:
        if "Could not find a Chroma collection" in str(e) or "does not exist" in str(e):
            raise CustomException(
                f"Vector store not found at '{VECTOR_DB_PATH}'. Provide text_chunks to create it.", 
                e
            ) from e
        
        error_message = CustomException("Failed to get or create Chroma vector store", e)
        logger.error(str(error_message))
        raise error_message from e