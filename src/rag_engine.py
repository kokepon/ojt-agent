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

    # Load documents with custom parsing to optimize embedding content
    import json
    from llama_index.core import Document

    documents = []
    for file_path in source_dir.glob("**/*.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)

                    # Determine content based on fields (heuristic or explicit type check if possible)
                    # Since we don't strictly know the type per line without context, we can infer or just use known fields.
                    # But we know the filename usually indicates type (glossary.jsonl, etc.)

                    content_parts = []

                    # Glossary
                    if "term" in data and "definition" in data:
                        content_parts.append(f"Term: {data.get('term')}")
                        content_parts.append(f"Definition: {data.get('definition')}")
                        if data.get("category"):
                            content_parts.append(f"Category: {data.get('category')}")
                        if data.get("synonyms"):
                            content_parts.append(f"Synonyms: {', '.join(data.get('synonyms'))}")

                    # Dataset
                    elif "name" in data and "description" in data:
                        content_parts.append(f"Dataset Name: {data.get('name')}")
                        content_parts.append(f"Description: {data.get('description')}")
                        if data.get("schema_info"):
                            content_parts.append(f"Schema: {data.get('schema_info')}")

                    # Rule
                    elif "title" in data and "rule_content" in data:
                        content_parts.append(f"Rule Title: {data.get('title')}")
                        content_parts.append(f"Content: {data.get('rule_content')}")
                        if data.get("context"):
                            content_parts.append(f"Context: {data.get('context')}")

                    # Analysis
                    elif "title" in data and "summary" in data:
                        content_parts.append(f"Analysis Title: {data.get('title')}")
                        content_parts.append(f"Summary: {data.get('summary')}")
                        if data.get("findings"):
                            content_parts.append(f"Findings: {data.get('findings')}")

                    # Fallback
                    else:
                        content_parts.append(str(data))

                    text_content = "\n".join(content_parts)

                    # Create Document
                    # Exclude metadata from embedding to focus on the text content
                    doc = Document(
                        text=text_content,
                        metadata=data,
                        excluded_embed_metadata_keys=list(data.keys()), # Exclude ALL metadata from embedding
                        excluded_llm_metadata_keys=["id", "created_at", "updated_at", "author"] # Exclude system fields from LLM context (if we used LLM)
                    )
                    documents.append(doc)

                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line in {file_path}")

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
