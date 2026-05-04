## 1. Phân bổ Module

| Thành viên | Module đảm nhiệm | Chi tiết công việc |
|:---|:---|:---|
| **Dũng** | **M1: Advanced Chunking**<br>**M5: Enrichment Pipeline** | - Implement Semantic, Hierarchical, Structure-Aware chunking.<br>- Implement Summarization, HyQA, Contextual Prepend, Auto Metadata.<br>- Đảm bảo dữ liệu đầu vào được làm giàu và phân đoạn tối ưu. |
| **Long** | **M2: Hybrid Search** | - Implement Vietnamese segmentation.<br>- Xây dựng BM25 Search và Dense Search (Qdrant).<br>- Kết hợp kết quả bằng Reciprocal Rank Fusion (RRF). |
| **Huy** | **M3: Reranking**<br>**M4: RAGAS Evaluation** | - Tích hợp Cross-encoder reranker và Flashrank.<br>- Xây dựng pipeline đánh giá RAGAS (4 metrics).<br>- Thực hiện Failure Analysis và Diagnostic Tree. |

## 2. Trách nhiệm chung (Nhóm)
- **B1: Pipeline chạy end-to-end:** Tất cả thành viên phối hợp để `src/pipeline.py` hoạt động mượt mà.
- **B2: RAGAS Score:** Mục tiêu đạt ít nhất 2 metrics ≥ 0.75.
- **B3: Failure Analysis:** Cùng phân tích các câu hỏi bị lỗi để cải thiện pipeline.
- **B4: Presentation:** Chuẩn bị báo cáo nhóm và slide trình bày.

## 3. Lý do phân bổ
- Tuân thủ quy định: Một người làm M5 kèm M1 (Dũng chọn cặp này để tập trung vào giai đoạn xử lý dữ liệu/Indexing).
- Phân chia theo luồng: 
    - **Dũng** phụ trách **Data/Indexing** (M1, M5).
    - **Long** phụ trách **Retrieval** (M2 - Core).
    - **Huy** phụ trách **Post-Retrieval & Eval** (M3, M4).
- Cân bằng khối lượng: Mỗi người đều đảm nhiệm các phần quan trọng và có khối lượng code tương đương nhau theo độ phức tạp của module.

## 4. Mục tiêu Bonus (+10 điểm)

Nhóm thống nhất mục tiêu đạt điểm bonus tối đa:
1. **RAGAS Faithfulness ≥ 0.85 (+5đ):** **Huy** tập trung tối ưu prompt evaluation và **Dũng** tối ưu chất lượng chunking.
2. **Enrichment Pipeline Integrated (+3đ):** **Dũng** đảm bảo M5 được tích hợp hoàn chỉnh vào `pipeline.py`.
3. **Latency Breakdown Report (+2đ):** **Long** và **Huy** thực hiện đo đạc và lập bảng thời gian thực thi cho từng bước trong pipeline.
