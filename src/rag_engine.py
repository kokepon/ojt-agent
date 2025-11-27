import os
from pathlib import Path
from typing import List
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
import qdrant_client
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "ojt_knowledge"
EMBEDDING_MODEL_NAME = "models/text-embedding-004"

def get_qdrant_client():
    return qdrant_client.QdrantClient(url=QDRANT_URL)

def setup_settings():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    Settings.embed_model = GeminiEmbedding(model_name=EMBEDDING_MODEL_NAME, api_key=api_key)
    Settings.llm = Gemini(api_key=api_key)

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
    query_engine = index.as_query_engine(similarity_top_k=top_k)

    response = query_engine.query(query)
    return str(response)
