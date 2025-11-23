import os
from pathlib import Path

current_dir = Path(__file__).parent

# ChromaDB settings
VECTOR_DB_PATH = os.path.join(current_dir, "../server/tools/rag/vector_db")
CHROMA_COLLECTION_NAME = "mcp_collection"

# Embedding model settings
EMBED_MODEL = "bge-m3:latest"
OLLAMA_BASE_URL = "http://localhost:11434"

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retriver Setting
TOP_K = 5

# Other paths
DATA_PATH=os.path.join(current_dir, "../server/tools/rag/data")
CACHE_PATH=os.path.join(current_dir, "../server/tools/rag/cache")

