import chromadb
from .config import BASE_DIR  # you might define BASE_DIR

CHROMA_PATH = Path(__file__).parent.parent.parent / "data" / "chroma_db"
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = chroma_client.get_collection("tourism_locations")