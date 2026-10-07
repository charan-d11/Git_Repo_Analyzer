import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

REPO_PATH        = os.path.join(BASE_DIR, "data", "repos")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index")

CHUNK_S = 1000
CHUNK_O = 200

SUPPORTED_EXT = ['.md', '.py']
