"""
Module 4: RAGAS Evaluation — 4 metrics + failure analysis.
============================================================
Measure first, optimize second — RAGAS Diagnostic Tree mapping.

Author : Nguyễn Hoàng Long
Test   : pytest tests/test_m4.py
"""

import os, sys, json
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """
    Run RAGAS evaluation with 4 core metrics.

    Metrics:
    - Faithfulness: Answer claims được context support không? Target ≥ 0.85
    - Answer Relevancy: Q&A cosine similarity. Target ≥ 0.80
    - Context Precision: Chunks retrieved có relevant không? Target ≥ 0.75
    - Context Recall: Đã retrieve đủ info cần thiết chưa? Target ≥ 0.75

    Args:
        questions: List of question strings.
        answers: List of answer strings.
        contexts: List of context lists (list of chunks per question).
        ground_truths: List of ground truth answer strings.

    Returns:
        Dict with 4 metric scores + per_question EvalResult list.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (faithfulness, answer_relevancy,
                                   context_precision, context_recall)
        from datasets import Dataset

        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })

        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
        )

        # Extract per-question results from dataframe
        df = result.to_pandas()
        per_question = []
        for _, row in df.iterrows():
            per_question.append(EvalResult(
                question=row.get("question", ""),
                answer=row.get("answer", ""),
                contexts=row.get("contexts", []),
                ground_truth=row.get("ground_truth", ""),
                faithfulness=float(row.get("faithfulness", 0)),
                answer_relevancy=float(row.get("answer_relevancy", 0)),
                context_precision=float(row.get("context_precision", 0)),
                context_recall=float(row.get("context_recall", 0)),
            ))

        return {
            "faithfulness": float(result.get("faithfulness", 0)),
            "answer_relevancy": float(result.get("answer_relevancy", 0)),
            "context_precision": float(result.get("context_precision", 0)),
            "context_recall": float(result.get("context_recall", 0)),
            "per_question": per_question,
        }

    except Exception:
        # Fallback: simple heuristic scoring khi RAGAS không khả dụng
        # (e.g., no OpenAI API key for judge model)
        per_question = []
        for i in range(len(questions)):
            ctx_text = " ".join(contexts[i]) if i < len(contexts) else ""
            gt = ground_truths[i] if i < len(ground_truths) else ""
            ans = answers[i] if i < len(answers) else ""

            # Simple keyword overlap scoring
            gt_words = set(gt.lower().split())
            ans_words = set(ans.lower().split())
            ctx_words = set(ctx_text.lower().split())

            # Faithfulness: how much of answer is supported by context
            faith = len(ans_words & ctx_words) / max(len(ans_words), 1)
            # Answer relevancy: answer-question overlap
            q_words = set(questions[i].lower().split())
            ar = len(ans_words & q_words) / max(len(q_words), 1)
            # Context precision: how relevant are retrieved chunks
            cp = len(ctx_words & gt_words) / max(len(ctx_words), 1)
            # Context recall: how much of ground truth is in context
            cr = len(ctx_words & gt_words) / max(len(gt_words), 1)

            per_question.append(EvalResult(
                question=questions[i],
                answer=ans,
                contexts=contexts[i] if i < len(contexts) else [],
                ground_truth=gt,
                faithfulness=min(faith, 1.0),
                answer_relevancy=min(ar, 1.0),
                context_precision=min(cp, 1.0),
                context_recall=min(cr, 1.0),
            ))

        # Aggregate scores
        n = max(len(per_question), 1)
        return {
            "faithfulness": sum(r.faithfulness for r in per_question) / n,
            "answer_relevancy": sum(r.answer_relevancy for r in per_question) / n,
            "context_precision": sum(r.context_precision for r in per_question) / n,
            "context_recall": sum(r.context_recall for r in per_question) / n,
            "per_question": per_question,
        }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """
    Analyze bottom-N worst questions using Diagnostic Tree (slide 7.2).

    Diagnostic mapping:
      faithfulness < 0.85     → "LLM hallucinating" → "Tighten prompt, lower temperature"
      context_recall < 0.75   → "Missing relevant chunks" → "Improve chunking or add BM25"
      context_precision < 0.75 → "Too many irrelevant chunks" → "Add reranking or metadata filter"
      answer_relevancy < 0.80 → "Answer doesn't match question" → "Improve prompt template"

    Args:
        eval_results: List of EvalResult from evaluate_ragas().
        bottom_n: Number of worst questions to analyze.

    Returns:
        List of failure analysis dicts with diagnosis and suggested_fix.
    """
    if not eval_results:
        return []

    # Diagnostic Tree mapping (ref: slide 7.2)
    DIAGNOSTIC_MAP = {
        "faithfulness": {
            "threshold": 0.85,
            "diagnosis": "LLM hallucinating — answer chứa thông tin không có trong context",
            "suggested_fix": "Tighten prompt ('Only use provided context'), lower temperature, dùng model ít hallucinate hơn",
        },
        "context_recall": {
            "threshold": 0.75,
            "diagnosis": "Missing relevant chunks — chunks đúng không được retrieve",
            "suggested_fix": "Đổi chunking (hierarchical), thêm BM25 (hybrid search), thử HyDE hoặc Multi-Query",
        },
        "context_precision": {
            "threshold": 0.75,
            "diagnosis": "Too many irrelevant chunks — retrieve quá nhiều noise",
            "suggested_fix": "Thêm reranking (cross-encoder), giảm top-K, tăng similarity threshold, metadata filtering",
        },
        "answer_relevancy": {
            "threshold": 0.80,
            "diagnosis": "Answer doesn't match question — LLM trả lời đúng nhưng không match",
            "suggested_fix": "Improve prompt template, kiểm tra context window overflow",
        },
    }

    # Calculate average score for each result
    scored_results = []
    for r in eval_results:
        avg = (r.faithfulness + r.answer_relevancy + r.context_precision + r.context_recall) / 4
        scored_results.append((avg, r))

    # Sort ascending (worst first) → take bottom_n
    scored_results.sort(key=lambda x: x[0])
    bottom = scored_results[:bottom_n]

    failures = []
    for avg_score, result in bottom:
        # Find worst metric
        metrics = {
            "faithfulness": result.faithfulness,
            "answer_relevancy": result.answer_relevancy,
            "context_precision": result.context_precision,
            "context_recall": result.context_recall,
        }
        worst_metric = min(metrics, key=metrics.get)
        worst_score = metrics[worst_metric]

        diag = DIAGNOSTIC_MAP[worst_metric]
        failures.append({
            "question": result.question,
            "avg_score": round(avg_score, 4),
            "worst_metric": worst_metric,
            "score": round(worst_score, 4),
            "diagnosis": diag["diagnosis"],
            "suggested_fix": diag["suggested_fix"],
            "all_scores": {k: round(v, 4) for k, v in metrics.items()},
        })

    return failures


def save_report(results: dict, failures: list[dict], path: str = "ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
