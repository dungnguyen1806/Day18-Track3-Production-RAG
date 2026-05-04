# Individual Reflection — Lab 18

**Tên:** Trần Thái Huy  
**Module phụ trách:** M3 / M4

---

## 1. Đóng góp kỹ thuật

- Module đã implement:
  - `M3: Reranking`
  - `M4: RAGAS Evaluation`
- Các hàm/class chính đã viết:
  - `CrossEncoderReranker`
  - `FlashrankReranker`
  - `benchmark_reranker`
  - `evaluate_ragas`
  - `failure_analysis`
  - tích hợp bước `LLM Generate` vào `pipeline.py`
- Số tests pass:
  - `M3: 5/5`
  - `M4: 4/4`
  - sau khi hoàn thiện toàn repo: `37/37`

## 2. Kiến thức học được

- Khái niệm mới nhất:
  - Sự khác nhau giữa `retrieval`, `reranking`, và `generation` trong một production RAG pipeline.
- Điều bất ngờ nhất:
  - `context_recall` có thể rất cao nhưng `context_precision` vẫn rất thấp. Điều này cho thấy pipeline có thể lấy đúng thông tin nhưng vẫn kéo theo quá nhiều noise.
- Kết nối với bài giảng:
  - Phần Hybrid Search, Reranking, và Error Tree / Failure Analysis trong các slide về Production RAG.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất:
  - Khi chạy end-to-end, pipeline không chỉ gặp vấn đề ở logic code mà còn có lỗi runtime thực tế như Docker/Qdrant, API compatibility, và RAGAS warning.
- Cách giải quyết:
  - Thêm `docker-compose.yml` để chạy Qdrant local.
  - Sửa `pipeline.py` để dùng `gpt-4o-mini` cho bước generate.
  - Vá `m2_search.py` để tương thích với version mới của `qdrant-client`.
  - Dùng failure analysis để đọc đúng nguyên nhân chính là `context_precision` thấp, thay vì chỉ nhìn score tổng.
- Thời gian debug:
  - Tương đối nhiều, chủ yếu ở phần chạy thực tế và đồng bộ giữa module test với pipeline thật.

## 4. Nếu làm lại

- Sẽ làm khác điều gì:
  - Mình sẽ chạy pipeline end-to-end sớm hơn thay vì chỉ nhìn test pass của từng module, vì nhiều lỗi chỉ lộ ra khi các module ghép với nhau.
- Module nào muốn thử tiếp:
  - Mình muốn tối ưu thêm phần retrieval precision, đặc biệt là cách giảm noise sau hybrid search và trước generation.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 4 |
| Code quality | 4 |
| Teamwork | 4 |
| Problem solving | 5 |
