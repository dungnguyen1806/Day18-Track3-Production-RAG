"""
Module 2: Hybrid Search — BM25 (Vietnamese) + Dense + RRF.
============================================================
Implement BM25 search with Vietnamese word segmentation,
Dense vector search via Qdrant, and Reciprocal Rank Fusion.

Author : Nguyễn Hoàng Long (2A202600160)
Test   : pytest tests/test_m2.py
"""

import os, sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, EMBEDDING_MODEL,
                    EMBEDDING_DIM, BM25_TOP_K, DENSE_TOP_K, HYBRID_TOP_K)


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict
    method: str  # "bm25", "dense", "hybrid"


# ─── Vietnamese Word Segmentation ────────────────────────


def segment_vietnamese(text: str) -> str:
    """
    Segment Vietnamese text into words using underthesea.

    Tại sao cần: BM25 cần word boundaries chính xác.
    "nghỉ phép" = 1 từ ghép, không phải 2 từ rời.
    Thiếu bước này → BM25 gần vô dụng cho tiếng Việt (ref: slide 5.2).

    Args:
        text: Raw Vietnamese text.

    Returns:
        Segmented text with underscores joining compound words.
        VD: "nghỉ phép năm" → "nghỉ_phép năm"
    """
    from underthesea import word_tokenize
    return word_tokenize(text, format="text")


# ─── BM25 Search (Sparse / Lexical) ─────────────────────


class BM25Search:
    """BM25Okapi search with Vietnamese word segmentation."""

    def __init__(self):
        self.corpus_tokens: list[list[str]] = []
        self.documents: list[dict] = []
        self.bm25 = None

    def index(self, chunks: list[dict]) -> None:
        """
        Build BM25 index from chunks.

        Pipeline: raw text → segment_vietnamese() → split by space → BM25Okapi.

        Args:
            chunks: List of {"text": str, "metadata": dict}
        """
        from rank_bm25 import BM25Okapi

        self.documents = chunks
        # Segment each chunk's text and tokenize by whitespace
        self.corpus_tokens = [
            segment_vietnamese(chunk["text"]).split()
            for chunk in chunks
        ]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = BM25_TOP_K) -> list[SearchResult]:
        """
        Search using BM25 over segmented Vietnamese text.

        Args:
            query: User query string.
            top_k: Number of top results to return.

        Returns:
            List of SearchResult sorted by BM25 score descending.
        """
        if self.bm25 is None or not self.documents:
            return []

        # Segment and tokenize the query the same way as the corpus
        tokenized_query = segment_vietnamese(query).split()
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices sorted by score descending
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        return [
            SearchResult(
                text=self.documents[i]["text"],
                score=float(scores[i]),
                metadata=self.documents[i].get("metadata", {}),
                method="bm25"
            )
            for i in top_indices
        ]


# ─── Dense Vector Search (Qdrant) ───────────────────────


class DenseSearch:
    """Dense vector search using sentence-transformers + Qdrant."""

    def __init__(self):
        from qdrant_client import QdrantClient
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._encoder = None

    def _get_encoder(self):
        """Lazy-load embedding model (bge-m3) to save memory."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
        return self._encoder

    def index(self, chunks: list[dict], collection: str = COLLECTION_NAME) -> None:
        """
        Encode chunks and upload to Qdrant vector database.

        Pipeline: texts → bge-m3 encode → PointStruct → upsert to Qdrant.

        Args:
            chunks: List of {"text": str, "metadata": dict}
            collection: Qdrant collection name.
        """
        from qdrant_client.models import Distance, VectorParams, PointStruct

        # Recreate collection (clean slate for each indexing run)
        self.client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )

        # Encode all chunk texts into dense vectors
        texts = [c["text"] for c in chunks]
        vectors = self._get_encoder().encode(texts, show_progress_bar=True)

        # Build Qdrant points with payload containing text + metadata
        points = [
            PointStruct(
                id=i,
                vector=vectors[i].tolist(),
                payload={**c.get("metadata", {}), "text": c["text"]}
            )
            for i, c in enumerate(chunks)
        ]

        # Upsert in batches of 100 to avoid payload limits
        batch_size = 100
        for start in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=collection,
                points=points[start:start + batch_size]
            )

    def search(self, query: str, top_k: int = DENSE_TOP_K,
               collection: str = COLLECTION_NAME) -> list[SearchResult]:
        """
        Search using dense vectors via Qdrant.

        Args:
            query: User query string.
            top_k: Number of top results to return.
            collection: Qdrant collection to search.

        Returns:
            List of SearchResult sorted by cosine similarity descending.
        """
        query_vector = self._get_encoder().encode(query).tolist()
        hits = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k
        )

        return [
            SearchResult(
                text=hit.payload.get("text", ""),
                score=hit.score,
                metadata={k: v for k, v in hit.payload.items() if k != "text"},
                method="dense"
            )
            for hit in hits
        ]


# ─── Reciprocal Rank Fusion (RRF) ───────────────────────


def reciprocal_rank_fusion(results_list: list[list[SearchResult]], k: int = 60,
                           top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
    """
    Merge multiple ranked lists using Reciprocal Rank Fusion.

    Formula: score(d) = Σ 1/(k + rank_i(d))
    where k=60 (standard constant), rank is 1-indexed.

    Ref: Cormack et al. (2009) — "Reciprocal Rank Fusion outperforms
    Condorcet and individual Rank Learning Methods"

    Args:
        results_list: List of ranked result lists (e.g., [bm25_results, dense_results]).
        k: RRF constant (default 60, production standard).
        top_k: Number of top merged results to return.

    Returns:
        Merged list of SearchResult with method="hybrid", sorted by RRF score desc.
    """
    # Accumulate RRF scores keyed by document text
    rrf_scores: dict[str, dict] = {}

    for result_list in results_list:
        for rank, result in enumerate(result_list):
            doc_key = result.text
            if doc_key not in rrf_scores:
                rrf_scores[doc_key] = {
                    "score": 0.0,
                    "metadata": result.metadata,
                    "original_score": result.score,
                }
            # RRF formula: 1/(k + rank), rank is 1-indexed → rank+1
            rrf_scores[doc_key]["score"] += 1.0 / (k + rank + 1)

    # Sort by RRF score descending and take top-k
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    return [
        SearchResult(
            text=doc_text,
            score=doc_info["score"],
            metadata=doc_info["metadata"],
            method="hybrid"
        )
        for doc_text, doc_info in sorted_docs[:top_k]
    ]


# ─── Hybrid Search (combines BM25 + Dense + RRF) ────────


class HybridSearch:
    """Combines BM25 + Dense + RRF. (Đã implement sẵn — dùng classes ở trên)"""
    def __init__(self):
        self.bm25 = BM25Search()
        self.dense = DenseSearch()

    def index(self, chunks: list[dict]) -> None:
        self.bm25.index(chunks)
        self.dense.index(chunks)

    def search(self, query: str, top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
        bm25_results = self.bm25.search(query, top_k=BM25_TOP_K)
        dense_results = self.dense.search(query, top_k=DENSE_TOP_K)
        return reciprocal_rank_fusion([bm25_results, dense_results], top_k=top_k)


if __name__ == "__main__":
    print(f"Original:  Nhân viên được nghỉ phép năm")
    print(f"Segmented: {segment_vietnamese('Nhân viên được nghỉ phép năm')}")

    # Quick BM25 test
    chunks = [
        {"text": "Nhân viên được nghỉ phép năm 12 ngày.", "metadata": {"source": "policy"}},
        {"text": "Mật khẩu thay đổi mỗi 90 ngày.", "metadata": {"source": "it"}},
        {"text": "Thời gian thử việc là 60 ngày.", "metadata": {"source": "hr"}},
    ]
    bm25 = BM25Search()
    bm25.index(chunks)
    results = bm25.search("nghỉ phép năm", top_k=3)
    print(f"\nBM25 results for 'nghỉ phép năm':")
    for r in results:
        print(f"  [{r.score:.4f}] {r.text}")
