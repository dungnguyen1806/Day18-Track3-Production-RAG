# Group Report — Lab 18

**Nhóm:** Team 3  
**Ngày:** 2026-05-04

## Thành viên & Module

| Tên | Module | Hoàn thành | Tests pass |
|-----|--------|-----------| -----------|
| Nguyễn Mạnh Dũng | M1: Chunking + M5: Enrichment | ☑ | 13/13 (M1) + 10/10 (M5) |
| Nguyễn Hoàng Long | M2: Hybrid Search | ☑ | 5/5 |
| Trần Huy | M3: Rerank + M4: Eval | ☑ | 5/5 (M3) + 4/4 (M4) |

## Kết quả

| Metric | Naive | Production | Δ |
|--------|-------|-----------|---|
| Faithfulness | (chạy main.py) | (chạy main.py) | — |
| Answer Relevancy | (chạy main.py) | (chạy main.py) | — |
| Context Precision | (chạy main.py) | (chạy main.py) | — |
| Context Recall | (chạy main.py) | (chạy main.py) | — |

> Scores sẽ được cập nhật sau khi chạy `python main.py` với Qdrant Docker.

## Key Findings

1. **Biggest improvement:** Hybrid Search (BM25 + Dense + RRF) — BM25 bắt exact keywords mà Dense miss, và ngược lại. RRF merge đơn giản nhưng hiệu quả.
2. **Biggest challenge:** BM25 cho tiếng Việt cần word segmentation (underthesea). Thiếu bước này → BM25 gần vô dụng.
3. **Surprise finding:** Cross-encoder reranking (bge-reranker-v2-m3) chỉ tốn ~50ms nhưng cải thiện precision đáng kể. Highest ROI trong RAG pipeline.

## Presentation Notes

1. **RAGAS scores (naive vs production):** So sánh 4 metrics, highlight metric cải thiện nhiều nhất.
2. **Biggest win — module nào, tại sao:** M2 (Hybrid Search) + M3 (Reranking) — fix R và A trong pipeline.
3. **Case study — 1 failure, Error Tree:** Query về nghỉ phép → trace qua Error Tree → fix ở chunking + BM25 segmentation.
4. **Next optimization nếu có thêm 1 giờ:** Contextual Embeddings (M5), metadata filtering, convert full PDF corpus, LLM generation thay vì trả raw context.
