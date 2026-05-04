# Individual Reflection — Lab 18

**Tên:** Nguyễn Mạnh Dũng
**Mã học viên:** 2A202600176
**Module phụ trách:** M1, M5

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M1 (Advanced Chunking), M5 (Enrichment Pipeline)
- Các hàm/class chính đã viết: 
  - M1: `chunk_semantic`, `chunk_hierarchical`, `chunk_structure_aware`, `compare_strategies`
  - M5: `summarize_chunk`, `generate_hypothesis_questions`, `contextual_prepend`, `extract_metadata`, `enrich_chunks`
- Số tests pass: 23/23

## 2. Kiến thức học được

- Khái niệm mới nhất: Semantic Chunking, Hierarchical Chunking (Parent-Child retrieval), và các kỹ thuật RAG Enrichment như Hypothetical Questions (HyQA), Contextual Prepend.
- Điều bất ngờ nhất: Chi phí indexing một lần cho việc enrichment (M5) có thể cải thiện đáng kể chất lượng của mọi query về sau. Đây là một khoản đầu tư trả trước (one-time cost) có ROI cao.
- Kết nối với bài giảng (slide nào): Slide về "Indexing Strategies" (M1) và "Query Transformations & Augmentation" (M5).

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Cân bằng giữa chất lượng và chi phí/tốc độ khi gọi LLM cho M5 (enrichment), đặc biệt là đảm bảo output của LLM nhất quán. Thêm vào đó là việc tuning `threshold` cho M1 (semantic chunking) để có các chunk tối ưu.
- Cách giải quyết: Sử dụng model `gpt-4o-mini` để tiết kiệm chi phí, kết hợp fallback sang các phương pháp extractive (không gọi LLM). Với chunking, đã thử nghiệm nhiều giá trị threshold và đánh giá thủ công chất lượng chunk để tìm ra con số phù hợp.
- Thời gian debug: Khoảng 3 giờ, chủ yếu là để xử lý các trường hợp output không nhất quán từ LLM và tinh chỉnh tham số cho các chiến lược chunking.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Xây dựng một hệ thống caching cho M5 (enrichment) để không phải xử lý lại những content đã có, giúp tiết kiệm thời gian và chi phí khi indexing lại bộ dữ liệu lớn.
- Module nào muốn thử tiếp: M2 (Hybrid Search), để hiểu sâu hơn về cách kết hợp các phương pháp retrieval khác nhau (sparse và dense) và tầm quan trọng của Reciprocal Rank Fusion (RRF).

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|---|---|
| Hiểu bài giảng | 5 |
| Code quality | 4 |
| Teamwork | 5 |
| Problem solving | 5 |
