# Individual Reflection — Lab 18

**Tên:** Nguyễn Hoàng Long  
**Mã học viên:** 2A202600160  
**Module phụ trách:** M2: Hybrid Search

---

## 1. Đóng góp kỹ thuật

- **Module đã implement:** M2 — Hybrid Search (BM25 Vietnamese + Dense Vector + RRF Fusion)
- **Các hàm/class chính đã viết:**
  - `segment_vietnamese()` — Vietnamese word segmentation bằng underthesea
  - `BM25Search.index()` + `BM25Search.search()` — BM25Okapi search trên text đã segment
  - `DenseSearch.index()` + `DenseSearch.search()` — Dense vector search qua Qdrant + bge-m3
  - `reciprocal_rank_fusion()` — RRF merge: `score(d) = Σ 1/(k + rank + 1)`
- **Hỗ trợ thêm:** Implement M3 (Reranking), M4 (Evaluation), M5 (Enrichment) cho nhóm
- **Số tests pass:** 5/5 (M2) — 32/32 tổng (M1+M2+M4+M5)

## 2. Kiến thức học được

- **Khái niệm mới nhất:** Reciprocal Rank Fusion (RRF) — cách merge multiple ranked lists đơn giản nhưng hiệu quả, production standard. Không cần training data.
- **Điều bất ngờ nhất:** BM25 cho tiếng Việt gần vô dụng nếu không có word segmentation. "nghỉ phép" phải được nhận diện là 1 từ ghép, không phải 2 từ riêng lẻ.
- **Kết nối với bài giảng:**
  - Slide 5.1-5.2: Hybrid Search = BM25 (exact keywords) + Dense (semantic match). BM25 cho tiếng Việt cần word segmentation trước.
  - Slide 5.3: RRF Fusion — `score(d) = Σ 1/(k + rank_i(d))`. Không cần training, production standard.
  - Slide 5.5: Vector DB cho Production → Qdrant (built-in hybrid + rich metadata filtering).

## 3. Khó khăn & Cách giải quyết

- **Khó khăn lớn nhất:** BM25 trả về empty results cho query "nghỉ phép" dù corpus có document liên quan. Root cause: với corpus rất nhỏ (3 docs), BM25Okapi IDF computation có thể cho score = 0.
- **Cách giải quyết:** Bỏ filter `scores[i] > 0` — trả về top-k kết quả bất kể score. Đây là approach đúng vì thresholding nên do caller quyết định, không phải search engine.
- **Thời gian debug:** ~15 phút — dùng debug script để trace underthesea segmentation output và BM25 scores.

## 4. Nếu làm lại

- **Sẽ làm khác điều gì:** Thêm metadata filtering vào DenseSearch.search() (filter theo `year`, `category`) — Qdrant hỗ trợ sẵn qua `query_filter`.
- **Module nào muốn thử tiếp:** M5 Enrichment — Contextual Embeddings (Anthropic style) rất ấn tượng: giảm 49% retrieval failure chỉ bằng 1 LLM call/chunk khi indexing.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 4 |
| Teamwork | 5 |
| Problem solving | 4 |
