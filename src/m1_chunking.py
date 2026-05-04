"""
Module 1: Advanced Chunking Strategies
=======================================
Implement semantic, hierarchical, và structure-aware chunking.
So sánh với basic chunking (baseline) để thấy improvement.

Test: pytest tests/test_m1.py
"""

import os, sys, glob, re
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (DATA_DIR, HIERARCHICAL_PARENT_SIZE, HIERARCHICAL_CHILD_SIZE,
                    SEMANTIC_THRESHOLD)


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str | None = None


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Load all markdown/text files from data/. (Đã implement sẵn)"""
    docs = []
    for fp in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(fp, encoding="utf-8") as f:
            docs.append({"text": f.read(), "metadata": {"source": os.path.basename(fp)}})
    return docs


# ─── Baseline: Basic Chunking (để so sánh) ──────────────


def chunk_basic(text: str, chunk_size: int = 500, metadata: dict | None = None) -> list[Chunk]:
    """
    Basic chunking: split theo paragraph (\\n\\n).
    Đây là baseline — KHÔNG phải mục tiêu của module này.
    (Đã implement sẵn)
    """
    metadata = metadata or {}
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for i, para in enumerate(paragraphs):
        if len(current) + len(para) > chunk_size and current:
            chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
            current = ""
        current += para + "\n\n"
    if current.strip():
        chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
    return chunks


# ─── Strategy 1: Semantic Chunking ───────────────────────


def chunk_semantic(text: str, threshold: float = SEMANTIC_THRESHOLD,
                   metadata: dict | None = None) -> list[Chunk]:
    """
    Split text by sentence similarity — nhóm câu cùng chủ đề.
    Tốt hơn basic vì không cắt giữa ý.

    Args:
        text: Input text.
        threshold: Cosine similarity threshold. Dưới threshold → tách chunk mới.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        List of Chunk objects grouped by semantic similarity.
    """
    metadata = metadata or {}
    # 1. Split text into sentences:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\n', text) if s.strip()]
    if not sentences:
        return []

    # 2. Encode sentences:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")  # fast
    embeddings = model.encode(sentences)

    # 3. Compare consecutive sentences and group:
    from numpy import dot
    from numpy.linalg import norm
    def cosine_sim(a, b): return dot(a, b) / (norm(a) * norm(b))

    chunks = []
    current_group = [sentences[0]]
    
    for i in range(1, len(sentences)):
        sim = cosine_sim(embeddings[i-1], embeddings[i])
        if sim < threshold:
            # End current chunk
            chunks.append(Chunk(
                text=" ".join(current_group),
                metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
            ))
            current_group = []
        current_group.append(sentences[i])
        
    # Last group
    if current_group:
        chunks.append(Chunk(
            text=" ".join(current_group),
            metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
        ))

    return chunks


# ─── Strategy 2: Hierarchical Chunking ──────────────────


def chunk_hierarchical(text: str, parent_size: int = HIERARCHICAL_PARENT_SIZE,
                       child_size: int = HIERARCHICAL_CHILD_SIZE,
                       metadata: dict | None = None) -> tuple[list[Chunk], list[Chunk]]:
    """
    Parent-child hierarchy: retrieve child (precision) → return parent (context).
    Đây là default recommendation cho production RAG.

    Args:
        text: Input text.
        parent_size: Chars per parent chunk.
        child_size: Chars per child chunk.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        (parents, children) — mỗi child có parent_id link đến parent.
    """
    metadata = metadata or {}
    parents_list = []
    children_list = []

    # 1. Split text into parents (using paragraph split then grouping):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    current_parent_text = ""
    parent_index = 0

    temp_parents_text = []
    for para in paragraphs:
        if len(current_parent_text) + len(para) > parent_size and current_parent_text:
            temp_parents_text.append(current_parent_text.strip())
            current_parent_text = ""
        current_parent_text += para + "\n\n"
    if current_parent_text.strip():
        temp_parents_text.append(current_parent_text.strip())

    for p_idx, p_text in enumerate(temp_parents_text):
        pid = f"parent_{p_idx}_{hash(p_text) % 10000}"
        parent = Chunk(
            text=p_text,
            metadata={**metadata, "chunk_type": "parent", "parent_id": pid, "chunk_index": p_idx}
        )
        parents_list.append(parent)

        # 2. Split each parent into children:
        # Simple sliding window for children
        for c_idx in range(0, len(p_text), child_size):
            c_text = p_text[c_idx:c_idx + child_size].strip()
            if c_text:
                child = Chunk(
                    text=c_text,
                    metadata={**metadata, "chunk_type": "child", "chunk_index": c_idx // child_size},
                    parent_id=pid
                )
                children_list.append(child)

    return parents_list, children_list


# ─── Strategy 3: Structure-Aware Chunking ────────────────


def chunk_structure_aware(text: str, metadata: dict | None = None) -> list[Chunk]:
    """
    Parse markdown headers → chunk theo logical structure.
    Giữ nguyên tables, code blocks, lists — không cắt giữa chừng.

    Args:
        text: Markdown text.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        List of Chunk objects, mỗi chunk = 1 section (header + content).
    """
    metadata = metadata or {}
    # 1. Split by markdown headers (H1, H2, H3):
    # Using a lookahead/lookbehind to keep the headers as separate parts in the split
    parts = re.split(r'(^#{1,3}\s+.+$)', text, flags=re.MULTILINE)
    
    chunks = []
    current_header = ""
    current_content = ""
    
    for part in parts:
        if not part.strip():
            continue
            
        if re.match(r'^#{1,3}\s+', part):
            # If we already have content from a previous section, save it
            if current_content.strip():
                chunks.append(Chunk(
                    text=f"{current_header}\n{current_content}".strip() if current_header else current_content.strip(),
                    metadata={**metadata, "section": current_header, "strategy": "structure", "chunk_index": len(chunks)}
                ))
            current_header = part.strip()
            current_content = ""
        else:
            current_content += part

    # Don't forget last section
    if current_content.strip() or current_header.strip():
        chunks.append(Chunk(
            text=f"{current_header}\n{current_content}".strip() if current_header else current_content.strip(),
            metadata={**metadata, "section": current_header, "strategy": "structure", "chunk_index": len(chunks)}
        ))

    return chunks


# ─── A/B Test: Compare All Strategies ────────────────────


def compare_strategies(documents: list[dict]) -> dict:
    """
    Run all strategies on documents and compare.

    Returns:
        {"basic": {...}, "semantic": {...}, "hierarchical": {...}, "structure": {...}}
    """
    results = {
        "basic": {"chunks": 0, "len": []},
        "semantic": {"chunks": 0, "len": []},
        "hierarchical": {"parents": 0, "children": 0, "len_child": []},
        "structure": {"chunks": 0, "len": []}
    }

    for doc in documents:
        text = doc["text"]
        meta = doc["metadata"]

        # Basic
        c_basic = chunk_basic(text, metadata=meta)
        results["basic"]["chunks"] += len(c_basic)
        results["basic"]["len"].extend([len(c.text) for c in c_basic])

        # Semantic
        c_semantic = chunk_semantic(text, metadata=meta)
        results["semantic"]["chunks"] += len(c_semantic)
        results["semantic"]["len"].extend([len(c.text) for c in c_semantic])

        # Hierarchical
        parents, children = chunk_hierarchical(text, metadata=meta)
        results["hierarchical"]["parents"] += len(parents)
        results["hierarchical"]["children"] += len(children)
        results["hierarchical"]["len_child"].extend([len(c.text) for c in children])

        # Structure
        c_structure = chunk_structure_aware(text, metadata=meta)
        results["structure"]["chunks"] += len(c_structure)
        results["structure"]["len"].extend([len(c.text) for c in c_structure])

    # Print Comparison Table
    print("\n" + "=" * 65)
    print(f"{'Strategy':<15} | {'Chunks':<10} | {'Avg Len':<10} | {'Min':<6} | {'Max':<6}")
    print("-" * 65)

    summary = {}
    for name, data in results.items():
        if name == "hierarchical":
            lengths = data["len_child"]
            count_str = f"{data['parents']}p/{data['children']}c"
        else:
            lengths = data["len"]
            count_str = str(data["chunks"])

        if lengths:
            avg_len = sum(lengths) / len(lengths)
            min_len = min(lengths)
            max_len = max(lengths)
        else:
            avg_len, min_len, max_len = 0, 0, 0

        print(f"{name:<15} | {count_str:<10} | {avg_len:<10.1f} | {min_len:<6} | {max_len:<6}")
        summary[name] = {
            "count": count_str,
            "avg": round(avg_len, 1),
            "min": min_len,
            "max": max_len
        }

    return summary


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    results = compare_strategies(docs)
    for name, stats in results.items():
        print(f"  {name}: {stats}")
