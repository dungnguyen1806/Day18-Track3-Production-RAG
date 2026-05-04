# Failure Analysis — Lab 18

**Nhóm:** Team 3  
**Thành viên:** Nguyễn Mạnh Dũng → M1+M5 · Nguyễn Hoàng Long → M2 · Trần Huy → M3+M4

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | (chờ pipeline chạy) | (chờ pipeline chạy) | — |
| Answer Relevancy | (chờ pipeline chạy) | (chờ pipeline chạy) | — |
| Context Precision | (chờ pipeline chạy) | (chờ pipeline chạy) | — |
| Context Recall | (chờ pipeline chạy) | (chờ pipeline chạy) | — |

> **Lưu ý:** Scores sẽ được cập nhật sau khi chạy `python main.py` với Qdrant Docker.

## Bottom-5 Failures

### #1
- **Question:** (sẽ điền sau khi chạy pipeline)
- **Expected:** —
- **Got:** —
- **Worst metric:** —
- **Error Tree:** Output sai → Context đúng? → Query OK? → Root cause:
- **Suggested fix:**

### #2
- **Question:** —
- **Worst metric:** —
- **Error Tree:** —
- **Suggested fix:**

### #3
- **Question:** —
- **Worst metric:** —
- **Error Tree:** —
- **Suggested fix:**

### #4
- **Question:** —
- **Worst metric:** —
- **Error Tree:** —
- **Suggested fix:**

### #5
- **Question:** —
- **Worst metric:** —
- **Error Tree:** —
- **Suggested fix:**

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
