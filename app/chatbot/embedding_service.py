"""
Embedding Service for the Markdown Knowledge Base.

This module reads markdown knowledge base files, chunks them,
generates embeddings, and builds a FAISS vector store.
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer
import json
import faiss
import pickle
import numpy as np
BASE_DIR = Path(__file__).resolve().parents[2]
#BASE_DIR = Path(__file__).resolve().parents[1]
_EMBEDDING_MODEL = None

KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"


def load_markdown_documents() -> list[dict]:
    """
    Load all markdown files from the knowledge base directory.

    Returns:
        list[dict]: Each document contains source filename and content.
    """
    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append({
            "source": file_path.name,
            "path": str(file_path),
            "content": content
        })

    if not documents:
        raise ValueError(
            f"No markdown documents found in: {KNOWLEDGE_BASE_DIR}"
        )

    return documents


def chunk_document(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80
) -> list[str]:
    """
    Split a document into overlapping word-based chunks.

    Args:
        text: Full document text.
        chunk_size: Number of words per chunk.
        overlap: Number of words shared between consecutive chunks.

    Returns:
        list[str]: Text chunks.
    """
    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks



def create_chunks(
    documents: list[dict]
) -> list[dict]:
    """
    Create chunk records from markdown documents.
    Includes basic deduplication to avoid repeated chunks.
    """
    all_chunks = []
    seen_chunks = set()
    chunk_id = 0

    for document in documents:
        document_chunks = chunk_document(
            text=document["content"]
        )

        for chunk in document_chunks:
            normalized_chunk = " ".join(
                chunk.lower().split()
            )

            if normalized_chunk in seen_chunks:
                continue

            seen_chunks.add(normalized_chunk)

            all_chunks.append({
                "chunk_id": chunk_id,
                "source": document["source"],
                "content": chunk
            })

            chunk_id += 1

    return all_chunks



def load_embedding_model(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> SentenceTransformer:
    """
    Load embedding model once and reuse it.
    """
    global _EMBEDDING_MODEL

    if _EMBEDDING_MODEL is not None:
        return _EMBEDDING_MODEL

    print(f"Loading embedding model: {model_name}")

    _EMBEDDING_MODEL = SentenceTransformer(model_name)

    return _EMBEDDING_MODEL


def generate_embeddings(
    chunks: list[dict],
    model: SentenceTransformer
) -> np.ndarray:
    """
    Generate embeddings for all chunk records.

    Args:
        chunks: Output from create_chunks()
        model: Loaded SentenceTransformer model

    Returns:
        numpy.ndarray
    """

    if not chunks:
        raise ValueError("No chunks provided for embedding generation.")

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")

    return embeddings


def save_chunks(
    chunks: list[dict],
    output_path: Path | None = None
) -> None:
    """
    Save chunk records to JSON.

    Args:
        chunks: Chunk records
        output_path: Optional override path
    """

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if output_path is None:
        output_path = VECTOR_STORE_DIR / "kb_chunks.json"

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(chunks)} chunks -> {output_path}"
    )



def save_chunk_id_map(
    chunks: list[dict],
    output_path: Path | None = None
) -> None:
    """
    Save FAISS index position to chunk metadata mapping.

    FAISS returns vector positions like 0, 1, 2.
    This file helps us map those positions back to the actual chunk.
    """

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if output_path is None:
        output_path = VECTOR_STORE_DIR / "chunk_id_map.pkl"

    chunk_id_map = {
        index: chunk
        for index, chunk in enumerate(chunks)
    }

    with open(output_path, "wb") as file:
        pickle.dump(chunk_id_map, file)

    print(
        f"Saved chunk id map -> {output_path}"
    )



def save_embeddings(
    embeddings: np.ndarray,
    output_path: Path | None = None
) -> None:
    """
    Save embeddings to disk.

    Args:
        embeddings: Numpy embedding matrix
        output_path: Optional override path
    """

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if output_path is None:
        output_path = VECTOR_STORE_DIR / "kb_embeddings.pkl"

    with open(output_path, "wb") as file:
        pickle.dump(embeddings, file)

    print(
        f"Saved embeddings -> {output_path}"
    )


def build_faiss_index(
    embeddings: np.ndarray
) -> faiss.Index:
    """
    Build FAISS similarity search index.

    Uses cosine similarity through
    normalized vectors + inner product.

    Args:
        embeddings: embedding matrix

    Returns:
        faiss.Index
    """

    if len(embeddings) == 0:
        raise ValueError(
            "No embeddings provided."
        )

    embeddings = embeddings.astype("float32")

    faiss.normalize_L2(embeddings)

    embedding_dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        embedding_dimension
    )

    index.add(embeddings)

    print(
        f"FAISS index created with "
        f"{index.ntotal} vectors."
    )

    return index

def save_faiss_index(
    index: faiss.Index,
    output_path: Path | None = None
) -> None:
    """
    Save FAISS index to disk.

    Args:
        index: FAISS index
        output_path: Optional override path
    """

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if output_path is None:
        output_path = VECTOR_STORE_DIR / "kb_index.faiss"

    faiss.write_index(
        index,
        str(output_path)
    )

    print(
        f"Saved FAISS index -> {output_path}"
    )


def build_vector_store() -> dict:
    """
    Build the complete vector store from markdown knowledge base files.

    Steps:
    1. Load markdown documents
    2. Chunk documents
    3. Load embedding model
    4. Generate embeddings
    5. Save chunks
    6. Save embeddings
    7. Build FAISS index
    8. Save FAISS index

    Returns:
        dict: Build summary
    """

    print("Starting vector store build...")

    documents = load_markdown_documents()

    chunks = create_chunks(
        documents=documents
    )

    if not chunks:
        raise ValueError(
            "No chunks created from knowledge base documents."
        )

    model = load_embedding_model()

    embeddings = generate_embeddings(
        chunks=chunks,
        model=model
    )

    save_chunks(
        chunks=chunks
    )

    save_chunk_id_map(
        chunks=chunks
    )

    save_embeddings(
        embeddings=embeddings
    )


    index = build_faiss_index(
        embeddings=embeddings
    )

    save_faiss_index(
        index=index
    )

    summary = {
    "success": True,
    "documents_loaded": len(documents),
    "chunks_created": len(chunks),
    "embedding_dimension": embeddings.shape[1],
    "faiss_vectors": index.ntotal,
    "chunk_id_map_created": True,
    "vector_store_path": str(VECTOR_STORE_DIR)
    }

    print("Vector store build completed.")
    print(summary)

    return summary


def rebuild_vector_store() -> dict:
    """
    Rebuild vector store from scratch.

    Deletes old vector store artifacts and creates new ones.
    Use this whenever knowledge base documents are added or updated.
    """

    print("Rebuilding vector store...")

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    artifact_files = [
    VECTOR_STORE_DIR / "kb_chunks.json",
    VECTOR_STORE_DIR / "kb_embeddings.pkl",
    VECTOR_STORE_DIR / "kb_index.faiss",
    VECTOR_STORE_DIR / "chunk_id_map.pkl"
    ]

    for file_path in artifact_files:
        if file_path.exists():
            file_path.unlink()
            print(f"Deleted old artifact: {file_path}")

    return build_vector_store()


if __name__ == "__main__":
    rebuild_vector_store()