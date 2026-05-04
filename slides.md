###### Production RAG

_AICB-P2T3 · Ngày 18 · Chương 4 — Agent Nâng Cao_

```
M.Sc Trần Minh Tú
VinUniversity · Phase 2 · Track 3 · Tuần 4
```

# ?

**HÃY SUY NGHĨ...**

_“Tại sao RAG pipeline demo chạy tốt_

_nhưng production accuracy chỉ đạt 60%_

_— ingestion hay retrieval đang giết bạn?”_

```
Giữ câu hỏi này trong đầu khi học bài hôm nay
```

**Nội dung bài học**

**1.** Tại sao Basic RAG thất bại?
**2.** Fix OFFLINE — Ingestion Pipeline
**3.** Enrichment Pipeline
**4.** Fix ONLINE — PreRAG
**5.** Fix ONLINE — Retrieval & Augment
    **6.** Fix ONLINE — Generate & PostRAG
    **7.** Evaluation — Đo lường RAG Pipeline
    **8.** Agentic RAG
    **9.** RAG vẫn chưa giải quyết được mọi thứ
    **10.** Demo & Thực hành


## 01

##### Tại sao Basic RAG thất bại?

Ingestion & Retrieval — failure nằm ở đâu trong pipeline?


**RAG Pipeline — Tổng quan ONLINE & OFFLINE**

```
Output
```
```
Query / Question RAG
```
```
Storage Layer ONLINE
```
```
OFFLINE
Data ProcessingData
```
```
Data→Data Processing→Storage
Layer. Chạy 1 lần (hoặc khi data thay
đổi). “Garbage in, garbage out.”
```
```
Query→RAG→Output. Chạy mỗi
query. Production accuracy chỉ 55–
65% — tại sao?
```
M.Sc Trần Minh Tú (VinUni) AICB · Ngày 18 Tuần 4 2 / 42


**OFFLINE Pipeline — Failure ở đâu?**

```
Data
Data
Processing Storage Layer
```
- Data sai
- Data có chất
    lượng thấp
       - Chunking
          Mismatch
       - Embedding
          Mismatch
       - Metadata thiếu
       - Parsing chưa tốt
          - Framework quản
             trị chưa tốt

```
Lưu ý: Trong thực tế: chỉ có ingestion pipeline là chưa đủ. Enrichment Pipeline sẽ
giúp chúng ta làm giàu thêm thông tin (contextual embeddings, metadata extraction,
data cleaning).
```

**ONLINE Pipeline — Nguyên nhân output sai ở từng bước**

```
Storage Layer
```
```
Query / Question PreRAG R A G PostRAG Output
```
```
Bước Vai trò Nguyên nhân output sai
PreRAG Xử lý query Query mơ hồ · Không rewrite · Vocabulary gap · Thiếu input guardrails
R Tìm chunks Chỉ 1 method · BM25 miss synonyms · Dense miss keywords · Thiếu metadata filter
A Ghép context Quá nhiều chunks · Lost in the middle · Context overflow · Thiếu reranking
G LLM trả lời Hallucinate · Prompt yếu · Temperature cao · Model không phù hợp
PostRAG Validate output Output không qua kiểm duyệt · Thiếu evaluation pipeline · Không có monitoring/feedback
loop
```
```
Lưu ý: Mỗi bước đều có thể khiến output sai. Production RAG cần fix toàn bộ chuỗi , không chỉ 1 bước.
```

**Error Tree Analysis — Log từng bước, tìm đúng chỗ sai**

```
Query PreRAG R·A·G PostRAG Output
```
```
Log: raw query Log: rewrittenquery + intent Log: chunks+ scores + eval scoresLog: answer Log: output+ feedback
```
```
Outputđúng?
```
```
OK
```
```
Yes
```
```
No Contextđúng?
```
```
Fix G : prompt
model / temperature
```
```
Yes
```
```
No rewrite OK?Query
```
```
Fix R/A : chunking
search / reranking
```
```
Yes
```
```
No Fixrewrite / HyDE PreRAG : query
```
```
vẫn sai? Fixquality / parsing Ingestion : data
```
**1.** Log mọi bước (query, chunks, scores, answer, feedback)→ **2.** Output sai? Đi ngược: PostRAG→R·A·G→
PreRAG→Data→ **3.** Dừng ở bước đầu tiên có vấn đề→fix đúng chỗ.


**Bằng chứng: Gap giữa Naive và Production RAG**

#### 60%

```
Naive RAG
Accuracy
```
#### 85%+

```
Production RAG
Accuracy
```
#### +25%

```
Improvement
khi optimize
```
```
Metric Naive RAG Production RAG Nguyên nhân cải thiện
```
```
Faithfulness ∼0.70 ≥0.85 Better prompt + reranking
Context Recall ∼0.55 ≥0.75 Hybrid search + enrichment
Context Precision ∼0.50 ≥0.75 Reranking + metadata filter
Answer Relevancy ∼0.65 ≥0.80 Query rewrite + augmentation
```

## 02

##### Fix OFFLINE — Ingestion

##### Pipeline

Data Processing: Chunking, Embedding & Enrichment


**Ingestion Pipeline — Mỗi bước fix 1 failure từ Section 1**

```
Document
PDF/HTML/MD
```
```
Parse
extract text
```
```
Clean
noise removal
```
```
Chunk
hierarchical
```
```
Metadata
date, source
```
```
Enrich
LLM context
Fix: Parsing
chưa tốt
```
```
Fix: Data
chất lượng thấp
Fix: Chunking
Mismatch
Fix: Metadata
thiếu
Fix: Embedding
Mismatch
```
```
Embed
text → vector
```
```
Index
Vector DB
```
```
Slide 1.2 liệt kê 5 OFFLINE failures.
Pipeline này fix từng failure một :
Parse→Clean→Chunk→Metadata
→Enrich.
```
```
Bỏ bước nào = để lọt failure đó vào
Vector DB.
```
```
Lưu ý: “Garbage in, garbage out”
— mỗi bước bỏ qua sẽ tích lũy lỗi.
Parse sai→chunk sai→embed sai
→retrieve sai→output sai.
```

**3 Chunking Strategies — So sánh**

```
Fixed-size Chunk 1 Chunk 2 Chunk 3 cắt giữa câu!
```
```
Semantic Chủ đề A Chủ đề B Chủ đề C nhóm theo similarity
```
```
Hierarchical
```
```
Parent chunk (full context)
```
```
Child 1 Child 2 Child 3
```
```
retrieve child, return parent
```
```
Hierarchical (parent-child) nên là de-
fault : chunks nhỏ cho retrieval preci-
sion + chunks lớn cho LLM context.
```
```
Fixed: 512 tokens, overlap 64
Semantic: cosine threshold 0.
Hierarchical: parent 2048, child 256
```

**Advanced Chunking — Structure-Aware & Late Chunking**

```
Parse markdown headers, HTML
tags, PDF sections rồi chunk theo
logical structure.
```
```
Giữ nguyên tables, code blocks, lists
— không cắt giữa chừng.
```
```
Ưu tiên khi corpus có structured doc-
uments (docs, API refs, manuals).
```
```
Dùng long-context embedding
model , chạy qua toàn bộ document
→ thu được token-level embed-
dings có full context.
```
```
Pool token embeddings theo chunk
boundaries→mỗi chunk embedding
mang context của cả document.
```
```
Khác naive: embed từng chunk riêng lẻ→“orphan”,
không biết xung quanh nói gì.
```
```
Yêu cầu: jina-embeddings-v2, nomic-embed.
Trade-off: tốn memory + latency cao hơn khi
indexing.
```
```
Lưu ý: Chunking strategy có impact lớn nhất lên RAG accuracy. Luôn A/B test chunking trước khi optimize retrieval
hay generation.
```
M.Sc Trần Minh Tú (VinUni) AICB · Ngày 18 Tuần 4 9 / 42


**Embedding Model Selection — Chọn đúng model cho use case**

**Model Dims Tiếng Việt Max Tokens Cost**

```
text-embedding-3-small 1536 OK 8191 $0.02/1M
text-embedding-3-large 3072 Tốt 8191 $0.13/1M
```
```
Cohere embed-v3 1024 Tốt 512 $0.10/1M
bge-m3 (open-source) 1024 Rất tốt 8192 Free
```
multilingual-e5-large 1024 Rất tốt 512 Free

```
Tiếng Việt → bge-m3 hoặc
multilingual-e5-large
Budget có →text-embedding-3-large
Production → Cohere embed-v
(built-in types)
```
```
Lưu ý: Đổi embedding model = re-
index toàn bộ. Chọn kỹ từ đầu!
Benchmark trên MTEB multilingual
leaderboard.
Note: Cohere Embed v4 đã hỗ trợ 128K tokens —
cân nhắc nếu cần long-context.
```

**Contextual Embeddings — Anthropic’s Contextual Retrieval**

```
Chunk gốc
“Nhân viên được nghỉ 12 ngày/năm.”
```
```
LLM prepend context
Claude Haiku / GPT-4o-mini
```
```
Contextual chunk
“Trích Chương 3 — Chính sách nghỉ phép
Sổ tay VinUni 2024. NV được nghỉ 12 ngày/năm.”
```
```
Embed→Index
```
```
Ý tưởng (Anthropic, Sep 2024) —
Trước khi embed mỗi chunk, dùng
LLM prepend 1 đoạn context ngắn
giải thích chunk nằm ở đâu trong
document.
```
```
Retrieval failure giảm 49% (alone)
Giảm 67% khi kết hợp Contextual
BM25 + Reranking
```
```
Lưu ý: Trade-off: +1 LLM call/chunk khi indexing
(one-time). Dùng model rẻ (Haiku, GPT-4o-mini).
```

**Multimodal Embeddings — Shared Latent Space**

```
Multimodal Embedding là gì? —
Chuyển data từ nhiều modalities
(text, image, audio) thành dense vec-
tors trong cùng 1 latent space.
```
```
Ví dụ: ảnh con chó và text “a happy golden retriever”
→2 vectors gần nhau trong shared space.
Cho phép: text query→retrieve cả text chunks lẫn
images.
```
**Model Modalities Note**

CLIP / SigLIP Text+Image Contrastive learning
Jina CLIP v2 Text+Image Multilingual
ColPali/ColQwen2 Full page Doc-native
Voyage MM 3 Text+Image API-based

**1. Describe then Embed** : Image→VLM mô tả→
embed text.
+Dùng existing text pipeline. –Mất spatial/visual
nuance.
**2. Native Multimodal** : Image+Text→shared vec-
tor space (CLIP-style).
+Giữ visual info, cross-modal retrieval.–Alignment
chưa perfect.
**3. Document-as-Image** (ColPali): Render page→
embed toàn bộ page image. Bypass OCR.
+Giữ layout/tables/figures. –Tốn storage, cần
GPU.

```
Lưu ý: Chỉ cần khi corpus có>20% visual con-
tent. Text-to-image retrieval accuracy thấp hơn text-
to-text 15–20%.
```

## 03

##### Enrichment Pipeline

Làm giàu chunks trước khi embed — Summarize, HyQA, Meta-

data


**Enrichment Pipeline — Tại sao cần “làm giàu” chunks?**

```
Raw
Chunk
```
```
Summarize
```
```
Hypothesis Q&A
```
```
Contextual
Prepend
```
```
Auto Metadata
```
```
Enriched
Chunk
```
```
Song song — LLM-powered, one-time, offline
```
```
Raw chunks thiếu context→embed-
ding chỉ capture surface meaning.
```
```
Enrichment = thêm thông tin trước
khi embed để vector representations
phong phú hơn.
```
```
4 techniques độc lập →chạy parallel
trên mỗi chunk.
```
```
Output merge: enriched_text + sum-
mary + questions + metadata→1 en-
riched chunk.
```

**Enrichment Techniques — 4 kỹ thuật chính**

```
LLM tạo summary ngắn cho mỗi chunk.
Embed summary thay vì (hoặc cùng với) raw chunk.
Ưu điểm: giảm noise, focus vào key info.
Dùng khi: chunks dài, nhiều filler text.
```
```
LLM generate câu hỏi mà chunk có thể trả lời.
Index cả questions lẫn chunk→query match tốt
hơn.
Ưu điểm: bridge vocabulary gap (giống HyDE
nhưng offline).
Dùng khi: user queries khác ngôn ngữ với docu-
ments.
```
```
Prepend context giải thích chunk nằm ở đâu trong
document.
Đã cover ở slide Contextual Embeddings.
Giảm 49% retrieval failure (alone).
```
```
LLM extract: topic, entities, date_range,
sentiment.
Gắn vào chunk metadata→enable rich filtering.
Dùng khi: corpus lớn, cần multi-faceted search.
```
```
Lưu ý: Enrichment = one-time cost khi indexing.
Dùng model rẻ (GPT-4o-mini, Haiku). ROI cao vì
cải thiện mọi query sau đó.
```

## 04

##### Fix ONLINE — PreRAG

Query Transform, Corrective RAG — fix trước khi search


**Query Transform — HyDE & Multi-Query**

```
HyDE
Query
```
```
Hypothetical Answer
```
```
Embed & Search
```
```
LLM gen
```
```
Multi-Query
Complex Query
```
```
Sub-Q1 Sub-Q2 Sub-Q3
```
```
Merge Results
```
```
HyDE — Generate hypothetical answer, embed
answer thay vì query. Bridges vocabulary gap.
```
```
Multi-Query — Decompose query thành sub-
queries, retrieve mỗi cái, merge. Recall tăng cho
multi-hop.
```
```
Lưu ý: HyDE tốn thêm 1 LLM call/query. Chỉ
dùng khi vocabulary mismatch nghiêm trọng.
```

**Corrective RAG & Adaptive Retrieval**

```
Query
```
```
Retrieve
```
```
Evaluate Quality
```
```
Generate Web Searchor Rewrite
```
```
good low
```
Nếu retrieval quality thấp:

1. Trigger **web search** (fallback)
2. Hoặc **query rewrite** rồi retry
3. Rồi mới generate

Tránh generate trên bad context

```
Route queries theo complexity:
Simple →direct LLM (no RAG)
Medium →standard RAG
Complex →full pipeline + rerank
```
Giảm latency **40%** trung bình


## 05

##### Fix ONLINE — Retrieval & Aug-

##### ment

Hybrid Search, Metadata Filtering & Reranking — fix R và A


**Hybrid Search — BM25 + Dense Vector Fusion**

```
User Query
```
```
BM25
exact keywords
```
```
Rank A
```
```
Dense Vector
semantic match
```
```
RRF Fusion Rank B
```
```
Top-K Results
```
```
Không cần GPU Cần embedding model
```
Merge rankings đơn giản: score( _d_ )=

```
∑ 1
k +rank i ( d ). Không cần training, production
standard.
```

**BM25 vs Dense — Khi nào dùng cái nào?**

**Tiêu chí BM25 Dense Vector Hybrid**

Exact keywords **Tốt Yếu Tốt**

```
Synonyms / paraphrase Yếu Tốt Tốt
Multilingual Yếu Tốt Tốt
```
```
GPU required Không Có Có
Latency <5ms ∼20ms ∼25ms
```
```
Lưu ý: BM25 cho tiếng Việt: cần word segmentation (underthesea, VnCoreNLP)
trước khi index. Thiếu bước này→BM25 gần vô dụng cho tiếng Việt.
```

**Beyond RRF — Tensor Fusion, Late Interaction & Learned Sparse**

```
Tensor Fusion là gì? — Thay
vì concatenate vectors (ghép nối),
tensor fusion tính outer product
giữa feature vectors từ các modali-
ties/signals khác nhau.
```
```
Tạo ra tensor đa chiều map mọi tương tác giữa
features của BM25 signal và Dense signal→cap-
ture cross-signal interactions mà RRF bỏ lỡ.
```
```
Query tokens↔doc tokens→ MaxSim per query
token.
Token-level matching chính xác hơn single-vector.
Pre-compute doc embeddings→vẫn fast retrieval.
Có thể thay thế cả bi-encoder + cross-encoder.
```
```
Method Precision Latency How
```
```
RRF Baseline ∼1ms Rank merge
Weighted Score +2–3% ∼1ms Score merge
SPLADE +5–8% ∼15ms Learned sparse
ColBERT +8–12% ∼50ms Late interact
Tensor Fusion +10–15% ∼80ms Outer product
```
```
Thay BM25 bằng learned sparse vectors.
Kết hợp: exact match + learned term expansion.
Dùng inverted index→fast như BM25.
```
```
Lưu ý: Tensor fusion cần labeled data (query-doc
pairs) để train outer product layer. Không có→ RRF
+ cross-encoder là đủ tốt.
```

**Metadata Filtering — Pre-filter trước khi search**

```
Gắn metadata vào mỗi chunk khi in-
dexing.
Filter trước khi vector search→giảm
search space, tăng precision.
```
**Metadata phổ biến:**

```
■ source: tên file/URL gốc
■ date: ngày tạo/cập nhật
■ category: policy, FAQ, manual...
■ language: ngôn ngữ
■ section: chapter/heading
```
```
#Qdrantmetadatafiltering
client.search(
collection_name="docs",
query_vector=embedding,
query_filter=Filter(
must=[FieldCondition(
key="year",
match=MatchValue(value=2024)
)]
),
limit=20
)
```
```
Lưu ý: Metadata filtering phụ thuộc vector DB.
Qdrant, Weaviate, Pinecone hỗ trợ tốt. Chroma hạn
chế hơn.
```

**Vector DB cho Production RAG**

```
DB Hybrid Search Metadata Filter Khi nào?
```
```
Qdrant Built-in Rich Default pick
Weaviate Built-in Rich GraphQL fans
Pinecone Sparse+ Good Managed/SaaS
Milvus Built-in Rich Large-scale, GPU
Neo4j Vector+Graph Cypher GraphRAG
pgvector Manual SQL Already Postgres
Chroma — Basic Prototype
FAISS — — Research only
```
```
Production : Qdrant hoặc Milvus (open-source, hybrid + metadata). Pinecone (man-
aged, zero-ops). GraphRAG : Neo4j (vector + graph traversal). Lab : Qdrant local
(Docker).
```

**Reranking — Highest ROI Optimization**

```
Retrieve top-20
```
```
Cross-Encoder
rerank
```
```
Pass top-3 → LLM
```
```
∼1ms
```
```
∼50ms
```
```
+15–25%
precision
```
```
Bi : encode riêng, fast (∼1ms), no interaction
Cross : encode cùng, chậm (∼50ms), accu-
rate hơn nhiều
```
```
Reranking Models — So sánh:
Model Cost Note
```
```
Cohere Rerank v3.5 API Production default
bge-reranker-v2-m3 Free Multilingual, tiếng Việt tốt
ms-marco-MiniLM-L-12 Free Nhẹ, nhanh, English
Jina Reranker v2 API Multilingual, 8K context
Flashrank Free Ultra-light,<5ms
LLM-as-Reranker $$$ GPT-4o/Claude rerank
```
```
Retrieve top-20 →Rerank→Keep top-3
→LLM generate
```
```
Lưu ý: 30–50ms overhead đổi lấy +15–25% precision.
Highest ROI trong RAG pipeline. Tiếng Việt→bge-
reranker-v2-m3.
```

**Augmentation — Nâng cao context trước khi đưa vào LLM**

```
NLI model kiểm tra entailment giữa query và chunk.
Filter chunks contradict →giảm hallucination.
Tools: cross-encoder/nli-deberta-v3-base.
```
```
Gắn source reference vào context.
Prompt: “Cite sources using [1], [2]...”
Output: answer + citations + source links.
```
```
Merge chunks từ nhiều sources (DB, web, API).
Resolve conflicts: newest wins hoặc LLM arbitrate.
Ref: MASS-RAG (multi-agent synthesis).
```
```
Chunks quá dài→ compress trước khi LLM.
Extractive: giữ relevant sentences.
Abstractive: LLM summarize context.
Tools: LongLLMLingua, ContextualCompression.
```
```
Lưu ý: Augmentation = bước giữa Retrieval và Generation. Thường bị skip nhưng impact lớn lên answer quality +
giảm token cost.
```

## 06

##### Fix ONLINE — Generate & Pos-

##### tRAG

Self-RAG, RAG-Fusion, Semantic Cache — fix G và validate out-

put


**Self-RAG, RAG-Fusion & Semantic Caching**

```
Self-RAG — LLM tự quyết khi nào retrieve. Fine-
tune model output special tokens ([Retrieve],
[IsRel],[IsSup]). Không hoạt động out-of-the-
box.
```
1. Generate **multiple query variants**
2. Retrieve cho mỗi variant→3. RRF merge

```
Semantic Cache — Cache theo semantic similar-
ity. Query mới similar>0.95→trả cache. Giảm
30–50% LLM calls.
```
**Pattern Cost Khi nào?**

```
HyDE $$ Vocab mismatch
Multi-query $$ Multi-hop Q
CRAG $$ Unreliable retrieval
Self-RAG $$$ Fine-tuned model
RAG-Fusion $$$ Max recall
Sem. Cache $ Repeated queries
```
```
Lưu ý: Đừng dùng tất cả cùng lúc! Chọn pattern
theo failure mode cụ thể của pipeline.
```

## 07

##### Evaluation — Đo lường RAG

##### Pipeline

Measure first, optimize second — RAGAS, TruLens & DeepEval


**RAGAS — 4 metrics đánh giá RAG quality**

```
Faithfulness
Answer claims được
context support không?
Target:≥0.85
```
```
Answer Relevancy
Q&A cosine similarity
Target:≥0.80
```
```
Context Precision
Chunks retrieved có
relevant không?
Target:≥0.75
```
```
Context Recall
Đã retrieve đủ
info cần thiết chưa?
Target:≥0.75
```
```
Generation quality Generation quality
```
```
Retrieval quality Retrieval quality
```
```
Lưu ý: RAGAS phụ thuộc judge model — scores brittle khi đổi judge. Luôn report
judge model version cùng với scores.
```

**RAGAS Diagnostic — Score thấp thì fix ở đâu?**

```
Context chứa info đúng nhưng LLM bịa thêm
→Tighten prompt (“Only use provided context”)
→Giảm temperature, model ít hallucinate hơn
Context không chứa info cần thiết
→Thực ra là Context Recall problem ↓
```
```
Chunks đúng tồn tại nhưng không được retrieve
→Đổi chunking (hierarchical)
→Thêm BM25 (hybrid search)
→Thử HyDE hoặc Multi-Query
Chunks đúng KHÔNG tồn tại trong DB
→Review chunking pipeline (cắt mất info)
→Document chưa được ingest
```
```
Retrieve quá nhiều irrelevant chunks
→Thêm reranking (cross-encoder)
→Giảm top-K, tăng similarity threshold
→Metadata filtering
```
```
LLM trả lời đúng nhưng không match câu hỏi
→Improve prompt template
→Kiểm tra context window overflow
```
```
Lưu ý: Luôn failure analysis (bottom-10 questions)
trước khi nhìn aggregate scores. Aggregate che
giấu failure patterns.
```

**RAGAS Evaluation — Code Pattern**

```
from ragas import evaluate
from ragas.metrics import (
faithfulness, answer_relevancy,
context_precision, context_recall,
)
dataset = {
"question": questions,
"answer": answers,
"contexts": retrieved_chunks,
"ground_truth": ground_truths,
}
result = evaluate(dataset,
metrics=[faithfulness,
answer_relevancy,
context_precision,
context_recall])
print (result) #DataFrame
```
**Workflow chuẩn:**

**1.** Chạy RAGAS **baseline** trước
**2.** Xem **bottom-5** (failure analysis)
**3.** Optimize theo failure mode cụ thể
**4.** Re-run RAGAS, so sánh

```
Faithfulness≥0.85, Answer Rele-
vancy≥0.80
Context Recall≥0.75
Luôn failure analysis trước aggregate
```

**Evaluation Frameworks — RAGAS vs TruLens vs DeepEval**

```
Dimension RAGAS TruLens DeepEval
```
```
Focus RAG pipeline eval Eval + Tracing (OTel) RAG + Agents + Chatbot
Metrics 4 core metrics RAG Triad 50+ metrics
Custom Hạn chế Feedback functions G-Eval, DAG, BaseMetric
Tracing Minimal OpenTelemetry spans @observe decorator
CI/CD Manual setup Moderate Native Pytest
Ground truth Không cần Không cần Cả hai
Setup ⋆Dễ nhất ⋆⋆Trung bình ⋆⋆Trung bình
GitHub ∼13k stars ∼3k stars ∼15k stars
Used by AWS, Databricks Snowflake, Equinix OpenAI, Google, Microsoft
```
```
Cả 3 đều open-source, LLM-as-a-Judge, reference-free. Cost = LLM API calls cho
judge model.
```

**Chọn Evaluation Framework nào?**

```
Khi nào:
✓Focus RAG quality
✓Setup nhanh 5 phút
✓Team nhỏ, MVP
```
```
Không phù hợp:
×Multi-agent, chatbot
×CI/CD phức tạp
```
```
Khi nào:
✓Cần tracing + eval
✓Debug chính xác step fail
✓Agentic multi-hop
```
```
Không phù hợp:
×Quick prototype
×Team không cần tracing
```
```
Khi nào:
✓AI stack phức tạp
✓CI/CD gate (Pytest)
✓Safety, MCP metrics
```
```
Không phù hợp:
×Chỉ eval RAG đơn giản
```
```
Prototype : RAGAS (nhanh, đủ dùng)→ Debug : +TruLens (tracing tìm bottleneck)
→ CI/CD : +DeepEval (regression gate). Các framework không loại trừ nhau —
nhiều team dùng kết hợp.
```

**Cost Estimation — 1M documents, bao nhiêu tiền?**

```
Embedding 1M chunks × $0.02/1M
tokens≈$10–50
Contextual embeddings: +$50–200
(GPT-4o-mini)
Vector DB storage: ∼$20–50/month
(Qdrant Cloud)
```
```
Embedding:∼$0.00002 · Reranking:
∼$0.001
LLM generation:∼$0.01–0.05
Total: ∼ $0.01–0.06/query
```
```
Naive RAG :∼$1,500/month
Production RAG : ∼$2,200/month
(+47%)
```
```
Accuracy 85% vs 60%→ít escalation
ROI dương sau 2–3 tháng
```
```
Dùng GPT-4o: chi phí×10–15.
```
```
Lưu ý: Semantic caching giảm 30–
50% LLM calls→tiết kiệm đáng kể khi
nhiều user hỏi tương tự.
```

## 08

##### Agentic RAG

Khi agent điều khiển RAG pipeline — từ static sang autonomous


**RAG Evolution — Từ Naive đến Agentic**

```
Naive RAG
static pipeline
```
```
Advanced RAG
hybrid + rerank
```
```
Modular RAG
composable
Agentic RAG
autonomous
Hôm nay: đây Next level
```
```
Agentic RAG là gì? — Agent tự
quyết định khi nào retrieve, query
nào, bao nhiêu lần, dùng tool nào.
```
```
4 agentic patterns: Reflection , Plan-
ning , Tool Use , Multi-Agent Collab-
oration.
```
```
Ref: Ehtesham et al., “Agentic Retrieval-Augmented
Generation” (2025, arxiv 2501.09136)
```
```
Static pipeline không đủ khi:
→Query cần multi-hop reasoning
→Retrieval lần 1 không đủ→cần it-
erative
→Cần kết hợp nhiều sources (DB +
web + API)
→ Cần self-correction khi context
kém
```

**Agentic RAG — 3 Kiến trúc chính**

```
Single-Agent Multi-Agent Hierarchical
```
```
Mô tả 1 agent điều phối toàn bộ
retrieval + routing
```
```
Nhiều agent chuyên biệt,
mỗi agent 1 data source
```
```
Agent cấp cao delegate
xuống agent cấp thấp
Ưu điểm Đơn giản, latency thấp Scalable, parallel pro-
cessing
```
```
Strategic oversight, reli-
able
Nhược Không scale cho multi-
domain
```
```
Coordination overhead Latency cao, phức tạp
```
```
Khi nào Simple QA, routing Multi-domain synthesis High-stakes (medical, le-
gal)
```
```
Multi-agent synthesis: agents chuyên biệt cho sum-
marization , extraction , reasoning →synthesis
stage tổng hợp.
Outperform strong RAG baselines trên 4 bench-
marks.
```
```
Dùng self-knowledge của model để filter retrieved
docs.
RL-based training→model biết “mình biết gì, không
biết gì”.
Giảm input documents + tăng generation quality.
Lưu ý: Khác với Skill-RAG (Wei 2026) ở Section 9 — paper khác,
cùng tên.
```

**Agentic RAG — Corrective & Adaptive (đã học) + mới**

```
✓ CRAG = Corrective RAG (slide PreRAG)
✓ Adaptive Retrieval = route by complexity
✓ Self-RAG = LLM tự quyết retrieve
✓ RAG-Fusion = multi-query + RRF
```
```
Đây chính là building blocks của Agentic RAG!
Production RAG + Agent orchestration = Agentic
RAG.
```
**1. Reflection** : Agent tự đánh giá output, retry nếu
kém
**2. Planning** : Decompose complex query thành sub-
tasks
**3. Tool Use** : Gọi SQL, web search, API dynamically
**4. Multi-Agent** : Agents chuyên biệt collaborate

```
Workflow patterns: Prompt Chaining, Routing,
Parallelization, Orchestrator-Workers, Evaluator-
Optimizer.
```
```
Lưu ý: Agentic RAG không phải lúc nào cũng
cần. Simple queries→Production RAG đủ. Chỉ
dùng khi multi-hop, multi-source, iterative.
```

## 09

##### RAG vẫn chưa giải quyết được

##### mọi thứ

Hidden State of Embeddings — khi vector similarity không đủ


**Tại sao RAG không thể đạt 100% accuracy?**

```
Nhiều retrieval failures không phải vì thiếu evidence
trong corpus.
```
```
Nguyên nhân thực: alignment gap giữa query và
evidence space.
```
```
Query formulation không match cách evidence được
biểu diễn trong vector space→cosine similarity cao
nhưng semantic mismatch.
```
```
“Query-evidence misalignment is a typed rather
than monolithic phenomenon” — có nhiều loại mis-
alignment khác nhau.
```
```
Skill-RAG dùng hidden-state prober (lightweight)
để detect failure state trước khi generate.
```
```
Khi detect failure→ Skill Router chọn 1 trong 4
skills:
```
**1.** Query Rewriting
**2.** Question Decomposition
**3.** Evidence Focusing
**4.** Exit (truly irreducible)

```
Mỗi skill chiếm vùng riêng biệt trong failure state
space→có thể phân loại và xử lý targeted.
```
```
Lưu ý: Implication: Không phải cứ thêm data hoặc đổi embedding model là fix được. Cần diagnose loại failure
trước rồi mới chọn đúng skill/technique.
```

**Fundamental Limitations — Embedding không capture hết**

**1. Temporal blindness** : Vector không có chiều thời
gian→doc 2022 và 2024 cùng score.
**2. Entity-swap** : “capital of France” vs “capital of
Germany”→embeddings gần nhau!
**3. Negation insensitivity** : “Approved” vs “Not ap-
proved”→cosine similarity cao.
**4. Stale embeddings** : Model version drift→vec-
tors incompatible.

```
Embedding-based hallucination detection có certi-
fied limits (arxiv 2512.15068).
NLI + similarity không đủ cho safety-critical.
```
```
✓Metadata filtering (temporal, source)
✓NLI verification (post-retrieval)
✓Failure-aware routing (Skill-RAG)
✓GraphRAG cho relational queries
✓Human-in-the-loop cho high-stakes
```
```
RAG là powerful nhưng không perfect. Hiểu limitations→design đúng: khi nào RAG đủ, khi nào cần GraphRAG,
khi nào cần human review.
```

## 10

##### Demo & Thực hành

Cá nhân implement modules — Nhóm ghép thành Production

RAG System


**Thực hành — Bức tranh lớn**

```
Cá nhân: Module 1Chunking Module 2Search Module 3Rerank Module 4Eval EnrichmentModule 5
```
```
Nhóm: Production RAG System = M1 + M2 + M3 + M4 + M5 + Deploy
```
```
Mỗi người implement 1 module hoàn
chỉnh.
Có scaffold code + TODO markers.
Chạy test riêng cho từng module.
```
```
Mục đích: hiểu sâu 1 phần, không bị overwhelm.
```
```
Ghép modules thành full pipeline.
Chạy RAGAS end-to-end, so sánh với
basic baseline.
Failure analysis + presentation 5 phút.
```
```
Mục đích: thấy bức tranh lớn, teamwork.
```

**Live Demo — Naive vs Production RAG**

**1. Pipeline A** (basic): paragraph chunking + dense-only→chạy RAGAS
**2. Pipeline B** (production): hierarchical chunks + hybrid search + Cohere Rerank
    →chạy RAGAS
**3. Pipeline C** (bonus): thêm contextual embeddings→so sánh thêm
**4. Failure analysis** : zoom bottom-5 questions — dùng Diagnostic Tree map
    failure→fix


**Bài tập cá nhân — 5 Modules (chọn 1, implement 1.5 giờ)**

**Module TODO Test pass criteria Điểm**

**M1: Chunking Semantic, hierarchical,
structure-aware. A/B test
vs basic baseline.**

```
3 advanced outputs + com-
parison table. Hierarchical có
parent/child.
```
```
20
```
**M2: Hybrid Search BM25 (Vietnamese segmenta-
tion) + Dense + RRF fusion.
Metadata filter.**

```
Retrieve top-20 cho 10
queries. BM25 + Dense +
Hybrid scores.
```
```
20
```
**M3: Reranking Integrate cross-encoder
reranker. Top-20** → **top-3.
Latency benchmark.**

```
Precision@3 improvement
≥ 15%. Latency < 100ms.
```
```
20
```
**M4: Evaluation RAGAS eval pipeline. 4 met-
rics. Failure analysis bottom-
10.**

```
RAGAS report + diagnostic
mapping cho bottom-10 ques-
tions.
```
```
20
```
**M5: Enrichment Summarize, HyQA, contextual
prepend, auto metadata ex-
traction.**

```
Enriched chunks có summary
+ questions + metadata.
```
```
20
```
```
Mỗi module có file riêng: m1_chunking.py,
m2_search.py, m3_rerank.py, m4_eval.py,
m5_enrichment.py.
Mỗi file có# TODO:markers chỉ rõ cần implement
gì.
```
```
Nhóm 5 người→mỗi người 1 module.
Nhóm 4→gộp M5 vào người làm M1.
Nhóm 3→gộp M4+M5, M1 do người mạnh nhất.
Làm 1 mình→chọn M1 hoặc M2 (core nhất).
```

**Bài tập nhóm — Ghép thành Production RAG System (30 phút)**

**Các bước ghép:**

**1. Integrate** : ghép M1→M5→M2→M3
    thành pipeline
**2. Run M4** : RAGAS eval end-to-end
**3. Compare** : basic baseline vs production
    pipeline
**4. Failure analysis** : bottom-5, map vào
    Error Tree
**5. Present** : 5 phút/nhóm — scores + 1
    failure case study

```
Lưu ý: Nếu 1 module chưa xong→dùng fallback imple-
mentation trong scaffold (basic version có sẵn). Nhóm
vẫn chạy được full pipeline.
```
```
GitHub repo chứa:
├── m1_chunking.py
├── m2_search.py
├── m3_rerank.py
├── m4_eval.py
├── m5_enrichment.py
├── pipeline.py(ghép)
├── ragas_report.json
├── failure_analysis.md
└── README.md
```
1. RAGAS scores (basic vs production)
2. Biggest improvement ở module nào?
3. 1 failure case study (Error Tree)
4. Nếu có thêm 1 giờ, sẽ optimize gì?


**Hệ thống chấm điểm — Cá nhân + Nhóm**

**Điểm cá nhân (60%):**

```
Tiêu chí Điểm
```
```
Module implementation đúng 15
Test pass criteria đạt 15
Vietnamese-specific handling 10
Code quality + comments 10
TODO markers hoàn thành 10
```
```
Subtotal cá nhân 60
```
```
Mỗi module cótest_m*.py.
Chạypytest test_m1.py→pass/fail.
CI check:rufflint + type hints.
```
```
Điểm nhóm (40%):
Tiêu chí Điểm
```
```
Pipeline chạy end-to-end 10
RAGAS≥0.75 (any metric) 10
Failure analysis có insight 10
Presentation rõ ràng 10
```
```
Subtotal nhóm 40
```
```
+5: RAGAS Faithfulness≥0.85
+3: Structure-aware chunking integrated
+2: Latency breakdown report
```
```
Lưu ý:Tổng: 100 + 10 bonus. Cá nhân 60% +
Nhóm 40%. Đảm bảo ai cũng contribute.
```

**Starter Code & Setup — Bắt đầu ngay**

```
git clone github.com/vinuni-aicb/lab18
├── main.py(entry point)
├── check_lab.py(kiểm tra)
├── data/(sample corpus)
├── test_set.json(20 Q&A)
├── src/m1..m5_*.py(TODO)
├── src/pipeline.py(ghép)
├── tests/test_m*.py(auto-grade)
├── analysis/(reports)
└── naive_baseline.py(basic)
```
1. docker compose up -d(Qdrant)
2. pip install -r requirements.txt
3. python naive_baseline.py(basic)
4. M￿ src/m*_*.py→tìm TODO
5. Implement→pytest tests/

```
Lưu ý: Chạynaive_baseline.pyTRƯỚC để có ba-
sic scores. Mọi improvement so sánh với baseline
này.
```

**Tổng kết — Key Takeaways**

**Những ý chính cần nhớ** trước khi sang bài tiếp theo

```
1
```
```
RAG = OFFLINE (Ingestion + Enrichment) + ONLINE (PreRAG→R→A→G→PostRAG)
— biết failure ở bước nào mới fix đúng chỗ
```
```
2
```
```
Fix OFFLINE : Chunking (hierarchical) + Embedding (chọn đúng model) + Enrichment
Pipeline (summarize, HyQA, contextual) = nền tảng
```
```
3
```
```
Fix ONLINE : PreRAG (query rewrite)→Hybrid Search + Reranking→ Augmentation (NLI,
citation, fusion)→Generate + PostRAG
```
```
4 Measure : RAGAS→Error Tree→Diagnostic Tree→đúng eval framework
```
```
5
```
```
Beyond : Agentic RAG (agent-controlled pipeline) + RAG có fundamental limits (embedding
```
M.Sc Trần Minh Tú (VinUni)alignment gap)→cần diagnose failure typeAICB · Ngày 18 Tuần 4 41 / 42


**Tiếp theo & Bài tập**

```
Ngày 19: GraphRAG & Knowledge
Graphs
```
```
“Khi user hỏi về mối quan hệ giữa
5 entities — flat RAG trả lời sai,
GraphRAG trả lời đúng — tại sao?”
```
```
■ Hoàn thành Lab 18: Production
RAG pipeline + RAGAS report
■ Đọc: Microsoft GraphRAG paper
(2024)
■ Optional: Skill-RAG (arxiv
2604.15771), SKILL-RAG (arxiv
2509.20377), MASS-RAG (arxiv
2604.18509)
```

### Hỏi & Đáp


#### Cảm ơn!

AICB-P2T3 · Ngày 18 · Production RAG


