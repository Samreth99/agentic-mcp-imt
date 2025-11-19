import os
from pathlib import Path

current_dir = Path(__file__).parent

CHROMA_PATH = os.path.join(current_dir, "../server/tools/rag/chroma_db")
EMBED_MODEL = "bge-m3:latest"
OLLAMA_BASE_URL = "http://localhost:11434"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DATA_PATH=os.path.join(current_dir, "../server/tools/rag/data")
CACHE_PATH=os.path.join(current_dir, "../server/tools/rag/cache")
