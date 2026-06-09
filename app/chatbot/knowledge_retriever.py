"""
Knowledge Retriever for the AI Customer Operations Agent.

This module loads the FAISS vector store and retrieves relevant
knowledge base chunks for a customer query.
"""
import numpy as np
from pathlib import Path
import pickle

import re

import faiss
from app.chatbot.schemas import KnowledgeChunk
from sentence_transformers import SentenceTransformer
from app.chatbot.schemas import RetrievalResult


BASE_DIR = Path(__file__).resolve().parents[2]

VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"

FAISS_INDEX_PATH = VECTOR_STORE_DIR / "kb_index.faiss"
CHUNK_ID_MAP_PATH = VECTOR_STORE_DIR / "chunk_id_map.pkl"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_EMBEDDING_MODEL = None


def load_faiss_index(
    index_path: Path | None = None
) -> faiss.Index:
    """
    Load FAISS index from disk.
    """

    if index_path is None:
        index_path = FAISS_INDEX_PATH

    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}. "
            "Run embedding_service.py first."
        )

    index = faiss.read_index(
        str(index_path)
    )

    return index


def load_chunk_id_map(
    map_path: Path | None = None
) -> dict:
    """
    Load FAISS index position to chunk metadata mapping.
    """

    if map_path is None:
        map_path = CHUNK_ID_MAP_PATH

    if not map_path.exists():
        raise FileNotFoundError(
            f"Chunk ID map not found: {map_path}. "
            "Run embedding_service.py first."
        )

    with open(map_path, "rb") as file:
        chunk_id_map = pickle.load(file)

    return chunk_id_map

def load_embedding_model() -> SentenceTransformer:
    """
    Load the same embedding model used during indexing.

    Returns:
        SentenceTransformer
    """

    global _EMBEDDING_MODEL

    if _EMBEDDING_MODEL is not None:
        return _EMBEDDING_MODEL

    print(
        f"Loading embedding model: "
        f"{EMBEDDING_MODEL_NAME}"
    )

    _EMBEDDING_MODEL = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    return _EMBEDDING_MODEL


def generate_query_embedding(
    query: str,
    model: SentenceTransformer
) -> np.ndarray:
    """
    Convert a customer query into a normalized embedding.

    IMPORTANT:
    Query embeddings must be normalized
    exactly like indexed embeddings.

    Args:
        query: Customer question
        model: Loaded embedding model

    Returns:
        np.ndarray
    """

    if not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    embedding = embedding.astype(
        "float32"
    )

    # IMPORTANT:
    # Match index normalization.
    faiss.normalize_L2(
        embedding
    )

    return embedding


def search_faiss(
    query_embedding: np.ndarray,
    index: faiss.Index,
    top_k: int = 5
) -> tuple[np.ndarray, np.ndarray]:
    """
    Search FAISS index.

    Args:
        query_embedding: normalized query vector
        index: loaded FAISS index
        top_k: number of results

    Returns:
        scores, indices
    """

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    return scores, indices


def retrieve_chunks(
    scores: np.ndarray,
    indices: np.ndarray,
    chunk_id_map: dict
) -> list[KnowledgeChunk]:
    """
    Convert FAISS search results into
    KnowledgeChunk objects.
    Args:
        scores: similarity scores
        indices: FAISS indices
        chunk_id_map: loaded chunk mapping
    Returns:
        list[KnowledgeChunk]
    """

    retrieved_chunks = []

    result_scores = scores[0]
    result_indices = indices[0]

    for score, index_position in zip(
        result_scores,
        result_indices
    ):

        if index_position == -1:
            continue

        chunk_data = chunk_id_map.get(
            int(index_position)
        )

        if not chunk_data:
            continue

        retrieved_chunks.append(
            KnowledgeChunk(
                chunk_id=chunk_data["chunk_id"],
                source=chunk_data["source"],
                content=chunk_data["content"],
                score=float(score)
            )
        )

    return retrieved_chunks


def build_context(
    chunks: list[KnowledgeChunk]
) -> str:
    """
    Combine retrieved chunks into a single context string
    that can be passed to Gemini later.

    Args:
        chunks: Retrieved knowledge chunks

    Returns:
        str
    """

    if not chunks:
        return ""

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"Source: {chunk.source}\n"
            #f"Relevance Score: {chunk.score:.4f}\n"
            f"Content:\n{chunk.content}"
        )

    return "\n\n---\n\n".join(context_parts)


def keyword_search(
    query: str,
    chunk_id_map: dict,
    max_results: int = 3
) -> list[KnowledgeChunk]:
    """
    Simple keyword search for exact or near-exact matches.

    This helps with banking terms that semantic search may miss,
    such as KYC, ATM, POS, BVN, Tier 1, Tier 2, Tier 3.

    Args:
        query: Customer query
        chunk_id_map: Loaded chunk map
        max_results: Maximum keyword results

    Returns:
        list[KnowledgeChunk]
    """

    if not query.strip():
        return []

    query_terms = set(
        re.findall(
            r"\b\w+\b",
            query.lower()
        )
    )

    results = []

    for _, chunk in chunk_id_map.items():
        content = chunk["content"]
        content_terms = set(
            re.findall(
                r"\b\w+\b",
                content.lower()
            )
        )

        matched_terms = query_terms.intersection(
            content_terms
        )

        if matched_terms:
            score = len(matched_terms) / max(
                len(query_terms),
                1
            )

            results.append(
                KnowledgeChunk(
                    chunk_id=chunk["chunk_id"],
                    source=chunk["source"],
                    content=chunk["content"],
                    score=float(score)
                )
            )

    results = sorted(
        results,
        key=lambda item: item.score,
        reverse=True
    )

    return results[:max_results]


def semantic_search(
    query: str,
    top_k: int = 5
) -> RetrievalResult:
    """
    Main retrieval entrypoint.

    Flow:
    Query
        ↓
    Query Embedding
        ↓
    FAISS Search
        ↓
    Keyword Search
        ↓
    Merge Results
        ↓
    Build Context
        ↓
    RetrievalResult
    """

    model = load_embedding_model()

    index = load_faiss_index()

    chunk_id_map = load_chunk_id_map()

    query_embedding = generate_query_embedding(
        query=query,
        model=model
    )

    scores, indices = search_faiss(
        query_embedding=query_embedding,
        index=index,
        top_k=top_k
    )

    semantic_chunks = retrieve_chunks(
        scores=scores,
        indices=indices,
        chunk_id_map=chunk_id_map
    )

    keyword_chunks = keyword_search(
        query=query,
        chunk_id_map=chunk_id_map,
        max_results=3
    )

    merged_chunks = semantic_chunks.copy()

    existing_ids = {
        chunk.chunk_id
        for chunk in merged_chunks
    }

    for chunk in keyword_chunks:

        if chunk.chunk_id not in existing_ids:
            merged_chunks.append(chunk)

    merged_chunks = sorted(
        merged_chunks,
        key=lambda x: x.score,
        reverse=True
    )

    context = build_context(
        merged_chunks
    )

    return RetrievalResult(
        query=query,
        chunks=merged_chunks,
        combined_context=context
    )


def test_retrieval() -> None:
    """
    Quick retrieval test.
    """

    query = "How do I block my card?"

    result = semantic_search(
        query=query
    )

    print("\nQUERY")
    print(query)

    print("\nTOP RESULTS")

    for chunk in result.chunks:

        print(
            f"\nSource: {chunk.source}"
        )

        print(
            f"Score: {chunk.score:.4f}"
        )

        print(
            chunk.content[:250]
        )

    print("\nCONTEXT")

    print(
        result.combined_context[:1000]
    )

if __name__ == "__main__":
    test_retrieval()