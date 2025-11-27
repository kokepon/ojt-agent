import os
from pathlib import Path
from typing import List
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms.gemini import Gemini  # Removed
from llama_index.core import Settings
import qdrant_client
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "ojt_knowledge"
# Using a multilingual model suitable for Japanese
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"

def get_qdrant_client():
    return qdrant_client.QdrantClient(url=QDRANT_URL)

def setup_settings():
    # Use local embedding model
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    # No LLM needed for retrieval only
    Settings.llm = None

def reset_index():
    client = get_qdrant_client()
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"Collection {COLLECTION_NAME} deleted.")

def build_index(source_dir: Path):

    setup_settings()
    client = get_qdrant_client()
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Load documents (JSONL files are treated as text by default, might need custom loader for better parsing)
    # For simplicity, we use SimpleDirectoryReader which reads files as text.
    # Ideally, we should parse JSONL and create Document objects with metadata.
    reader = SimpleDirectoryReader(input_dir=str(source_dir), recursive=True)
    documents = reader.load_data()

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )
    print(f"Index built with {len(documents)} documents.")

def search(query: str, top_k: int = 5) -> str:
    setup_settings()
    client = get_qdrant_client()
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)

    # Load index from vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Use retriever instead of query engine (no LLM synthesis)
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)

    # Format results
    results = []
    for node in nodes:
        results.append(f"Content: {node.text}\nScore: {node.score}")

    return "\n\n".join(results)
