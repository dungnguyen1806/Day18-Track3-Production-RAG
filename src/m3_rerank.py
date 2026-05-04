"""
Module 3: Reranking — Cross-encoder top-20 → top-3 + latency benchmark.
=========================================================================
Highest ROI optimization trong RAG pipeline: 30-50ms overhead → +15-25% precision.

Author : Nguyễn Hoàng Long
Test   : pytest tests/test_m3.py
"""

import os, sys, time
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RERANK_TOP_K


@dataclass
class RerankResult:
    text: str
    original_score: float
    rerank_score: float
    metadata: dict
    rank: int


class CrossEncoderReranker:
    """
    Cross-encoder reranker using BAAI/bge-reranker-v2-m3.

    Bi-encoder: encode riêng, fast (~1ms), no interaction.
    Cross-encoder: encode cùng query+doc, chậm (~50ms), nhưng accurate hơn nhiều.

    Tiếng Việt → bge-reranker-v2-m3 (multilingual, tốt cho Vietnamese).
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy-load cross-encoder model."""
        if self._model is None:
            try:
                # Option A: FlagEmbedding (preferred cho bge-reranker)
                from FlagEmbedding import FlagReranker
                self._model = FlagReranker(self.model_name, use_fp16=True)
                self._model_type = "flag"
            except ImportError:
                try:
                    # Option B: sentence-transformers CrossEncoder
                    from sentence_transformers import CrossEncoder
                    self._model = CrossEncoder(self.model_name)
                    self._model_type = "cross"
                except Exception:
                    self._model = None
                    self._model_type = "none"
        return self._model

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        """
        Rerank documents using cross-encoder: top-20 → top-k.

        Flow: (query, doc) pairs → cross-encoder scores → sort → top-k.

        Args:
            query: User query string.
            documents: List of {"text": str, "score": float, "metadata": dict}
            top_k: Number of top results to keep after reranking.

        Returns:
            List of RerankResult sorted by rerank_score descending.
        """
        if not documents:
            return []

        model = self._load_model()

        # Build query-document pairs
        pairs = [(query, doc["text"]) for doc in documents]

        if model is not None and hasattr(self, '_model_type'):
            if self._model_type == "flag":
                # FlagReranker: compute_score returns list of floats
                scores = model.compute_score(pairs)
                if isinstance(scores, (int, float)):
                    scores = [scores]
            elif self._model_type == "cross":
                # CrossEncoder: predict returns numpy array
                scores = model.predict(pairs).tolist()
                if isinstance(scores, (int, float)):
                    scores = [scores]
            else:
                # Fallback: use original scores
                scores = [doc.get("score", 0.0) for doc in documents]
        else:
            # No model available — use original scores as rerank scores
            scores = [doc.get("score", 0.0) for doc in documents]

        # Combine scores with documents and sort
        scored_docs = list(zip(scores, documents))
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Return top-k as RerankResult
        return [
            RerankResult(
                text=doc["text"],
                original_score=doc.get("score", 0.0),
                rerank_score=float(score),
                metadata=doc.get("metadata", {}),
                rank=i
            )
            for i, (score, doc) in enumerate(scored_docs[:top_k])
        ]


class FlashrankReranker:
    """Lightweight alternative (<5ms). Optional."""

    def __init__(self):
        self._model = None

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        """Rerank using Flashrank (ultra-lightweight, <5ms)."""
        if not documents:
            return []

        try:
            from flashrank import Ranker, RerankRequest
            if self._model is None:
                self._model = Ranker()
            passages = [{"text": d["text"]} for d in documents]
            request = RerankRequest(query=query, passages=passages)
            results = self._model.rerank(request)

            return [
                RerankResult(
                    text=r["text"],
                    original_score=documents[i].get("score", 0.0) if i < len(documents) else 0.0,
                    rerank_score=r.get("score", 0.0),
                    metadata=documents[i].get("metadata", {}) if i < len(documents) else {},
                    rank=i
                )
                for i, r in enumerate(results[:top_k])
            ]
        except ImportError:
            # Flashrank not installed — return original order
            return [
                RerankResult(
                    text=doc["text"],
                    original_score=doc.get("score", 0.0),
                    rerank_score=doc.get("score", 0.0),
                    metadata=doc.get("metadata", {}),
                    rank=i
                )
                for i, doc in enumerate(documents[:top_k])
            ]


def benchmark_reranker(reranker, query: str, documents: list[dict], n_runs: int = 5) -> dict:
    """
    Benchmark reranker latency over n_runs.

    Args:
        reranker: CrossEncoderReranker or FlashrankReranker instance.
        query: Query string to benchmark with.
        documents: Documents to rerank.
        n_runs: Number of benchmark runs.

    Returns:
        {"avg_ms": float, "min_ms": float, "max_ms": float}
    """
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        reranker.rerank(query, documents)
        elapsed = (time.perf_counter() - start) * 1000  # convert to ms
        times.append(elapsed)

    return {
        "avg_ms": sum(times) / len(times) if times else 0,
        "min_ms": min(times) if times else 0,
        "max_ms": max(times) if times else 0,
    }


if __name__ == "__main__":
    query = "Nhân viên được nghỉ phép bao nhiêu ngày?"
    docs = [
        {"text": "Nhân viên được nghỉ 12 ngày/năm.", "score": 0.8, "metadata": {}},
        {"text": "Mật khẩu thay đổi mỗi 90 ngày.", "score": 0.7, "metadata": {}},
        {"text": "Thời gian thử việc là 60 ngày.", "score": 0.75, "metadata": {}},
    ]
    reranker = CrossEncoderReranker()
    results = reranker.rerank(query, docs)
    for r in results:
        print(f"[{r.rank}] {r.rerank_score:.4f} | {r.text}")

    bench = benchmark_reranker(reranker, query, docs)
    print(f"\nBenchmark: {bench}")
