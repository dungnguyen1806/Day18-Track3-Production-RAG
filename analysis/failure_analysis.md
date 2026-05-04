# Failure Analysis — Lab 18

**Nhóm:** Team 3  
**Thành viên:** Nguyễn Mạnh Dũng → M1+M5 · Nguyễn Hoàng Long → M2 · Trần Huy → M3+M4

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | 1.0000 | 0.8940 | -0.1060 |
| Answer Relevancy | 0.6643 | 0.7508 | +0.0865 |
| Context Precision | 0.0617 | 0.0724 | +0.0107 |
| Context Recall | 0.9800 | 0.9550 | -0.0250 |

> **Nhận xét ngắn:** Production đã kéo `answer_relevancy` vượt `0.75`, nhưng `context_precision` vẫn rất thấp nên retrieval còn mang theo nhiều noise.

## Bottom-5 Failures

### #1
- **Question:** Mật khẩu cần thay đổi sau bao lâu?
- **Expected:** Khoảng 90 ngày
- **Got:** Answer có liên quan nhưng context lẫn nhiều chunk không cần thiết
- **Worst metric:** `context_precision = 0.0511`
- **Error Tree:** Output chưa hẳn sai hoàn toàn → Context không đủ sạch → Root cause: retrieval còn kéo nhiều noise
- **Suggested fix:** Giảm top-K sau hybrid search, thêm metadata filtering theo domain `it`, siết rerank score threshold

### #2
- **Question:** Quy định bảo vệ dữ liệu cá nhân được ban hành năm nào?
- **Worst metric:** `context_precision = 0.1059`
- **Error Tree:** Output gần đúng nhưng context trộn cả policy HR và legal → Root cause: hybrid retrieval recall cao nhưng chưa đủ selective
- **Suggested fix:** Tách corpus theo loại tài liệu, thêm metadata `category=legal`, rerank mạnh hơn cho legal queries

### #3
- **Question:** Dữ liệu cá nhân bao gồm những loại nào?
- **Worst metric:** `context_precision = 0.0846`
- **Error Tree:** Context có chứa đáp án nhưng bị kèm nhiều đoạn giải thích khác → Root cause: top contexts quá rộng
- **Suggested fix:** Giảm số context đưa vào answer generation, ưu tiên chunk ngắn và tập trung hơn

### #4
- **Question:** Thời gian thử việc là bao lâu?
- **Worst metric:** `context_precision = 0.0526`
- **Error Tree:** Output đúng, context đúng, nhưng kèm thêm chunk không liên quan → Root cause: precision thấp dù recall cao
- **Suggested fix:** Tăng trọng số rerank cho exact-match chunk, hạ hybrid top-K trước rerank

### #5
- **Question:** Nhân viên được nghỉ phép bao nhiêu ngày mỗi năm?
- **Worst metric:** `context_precision = 0.0677`
- **Error Tree:** Output đúng, query đơn giản, nhưng context vẫn còn noise → Root cause: retrieve nhiều hơn mức cần thiết
- **Suggested fix:** Chỉ giữ top-1 hoặc top-2 context sau rerank cho câu hỏi factoid đơn giản

## Case Study (presentation)

**Question:** "Nhân viên được nghỉ phép bao nhiêu ngày mỗi năm?"

**Error Tree walkthrough:**
1. Output đúng? → Kiểm tra answer có chứa "12 ngày" không
2. Context đúng? → Kiểm tra chunks retrieved có chứa chương 2 (chính sách nghỉ phép)
3. Query rewrite OK? → Query đơn giản, không cần rewrite
4. Fix ở bước: Nếu context sai → cải thiện chunking (hierarchical) + BM25 Vietnamese segmentation

**Nếu có thêm 1 giờ:**
- Thêm Contextual Embeddings (M5) vào pipeline — giảm 49% retrieval failure
- Implement metadata filtering theo category (policy, it, hr, legal)
- Convert full PDF files sang markdown để có corpus phong phú hơn
- Fine-tune prompt template cho LLM generation
