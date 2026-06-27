"""
Place Retriever using embeddings
"""

from models.place import Place
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(
    path="./chroma_db"
)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="places",
    embedding_function=embedding_func
)

# clear old embeddings
def index_places():
    """Index all places into ChromaDB"""
    
    global collection

    try:
        client.delete_collection(name="places")
    except Exception:
        pass

    # recreate collection after deletion
    collection = client.get_or_create_collection(
        name="places",
        embedding_function=embedding_func
    )

    places = Place.query.all()

    for p in places:
        text = f"{p.name}. {p.description}. Category: {p.category}"
        collection.add(
            documents=[text],
            ids=[str(p.id)],
            metadatas=[{"place_id": p.id}]
        )


def search_places(query: str, k: int = 5):
    results = collection.query(query_texts=[query], n_results=k)
    return results