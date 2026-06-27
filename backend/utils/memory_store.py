"""
Persistent Memory Store using ChromaDB
"""

import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(
    path="./memory_db"
)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="chat_memory",
    embedding_function=embedding_func
)


def store_message(session_id: str, role: str, content: str):
    collection.add(
        documents=[content],
        metadatas=[{"session_id": session_id, "role": role}],
        ids=[f"{session_id}_{role}_{hash(content)}"]
    )


def retrieve_memory(session_id: str, query: str, k: int = 3):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    filtered = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        if meta["session_id"] == session_id:
            filtered.append(doc)

    return filtered