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
| Faithfulness | 1.0000 | 0.8940 | -0.1060 |
| Answer Relevancy | 0.6643 | 0.7508 | +0.0865 |
| Context Precision | 0.0617 | 0.0724 | +0.0107 |
| Context Recall | 0.9800 | 0.9550 | -0.0250 |

> Production pipeline đã cải thiện `answer_relevancy`, nhưng precision của context vẫn là nút thắt lớn nhất.

## Key Findings

1. **Biggest improvement:** `answer_relevancy` tăng từ `0.6643` lên `0.7258`, cho thấy pipeline production trả lời bám câu hỏi hơn baseline.
2. **Biggest challenge:** `context_precision` vẫn rất thấp (`0.0721`), nghĩa là retrieval vẫn kéo theo nhiều chunk không liên quan.
3. **Surprise finding:** Dù đã có reranking, recall vẫn cao hơn nhiều so với precision. Bài toán hiện tại không phải thiếu thông tin, mà là lọc chưa đủ gắt.

## Presentation Notes

1. **RAGAS scores (naive vs production):** Highlight `answer_relevancy` tăng, nhưng precision vẫn thấp.
2. **Biggest win — module nào, tại sao:** M3 + bước LLM generation làm câu trả lời khớp câu hỏi hơn.
3. **Case study — 1 failure, Error Tree:** Query về mật khẩu hoặc nghỉ phép cho thấy root cause chính là noisy context.
4. **Next optimization nếu có thêm 1 giờ:** metadata filtering, giảm top-K trước hoặc sau rerank, prompt generation chặt hơn, mở rộng corpus legal/policy sạch hơn.
