"""Batch evaluation script: load evaluation_dataset.txt and score every question end-to-end."""

from __future__ import annotations

import argparse
import json
import os
import statistics
from pathlib import Path

from llm_client import LLMClient, LLMConfig
from rag_client import RAGClient, RAGConfig
from ragas_evaluator import RagasEvaluator


def parse_evaluation_dataset(path: Path) -> list[dict[str, str]]:
    """Parse the Q: / Expected: block format used in evaluation_dataset.txt."""
    questions: list[dict[str, str]] = []
    current_q: str | None = None
    current_e: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("Q:"):
            current_q = line[2:].strip()
            current_e = None
        elif line.startswith("Expected:") and current_q:
            current_e = line[len("Expected:"):].strip()
            questions.append({"question": current_q, "expected": current_e})
            current_q = None
            current_e = None

    return questions


def run_batch(
    eval_path: Path,
    top_k: int = 4,
    mission: str | None = None,
    output_json: Path | None = None,
) -> None:
    questions = parse_evaluation_dataset(eval_path)
    if not questions:
        print("No Q:/Expected: pairs found in evaluation_dataset.txt.")
        return

    rag = RAGClient(RAGConfig())
    llm = LLMClient(LLMConfig())
    evaluator = RagasEvaluator()

    rows: list[dict] = []
    metric_keys = ["answer_relevancy", "faithfulness", "context_precision"]

    print(f"\nEvaluating {len(questions)} question(s) …\n")
    print("-" * 90)

    for i, item in enumerate(questions, start=1):
        q = item["question"]
        expected = item.get("expected", "")

        context, chunks = rag.retrieve_context(question=q, top_k=top_k, mission=mission)
        answer = llm.answer_question(question=q, context=context)
        scores = evaluator.evaluate_answer(
            question=q,
            answer=answer,
            contexts=[c.text for c in chunks],
            reference=expected if expected else None,
        )
        llm.reset_history()

        row = {
            "id": i,
            "question": q,
            "answer": answer,
            "answer_relevancy": scores.get("answer_relevancy", 0.0),
            "faithfulness": scores.get("faithfulness", 0.0),
            "context_precision": scores.get("context_precision", 0.0),
            "eval_mode": scores.get("mode", "unknown"),
        }
        rows.append(row)

        print(f"Q{i}: {q}")
        print(f"  Answer      : {answer[:120].replace(chr(10), ' ')}{'...' if len(answer) > 120 else ''}")
        print(f"  Relevancy   : {row['answer_relevancy']:.4f}")
        print(f"  Faithfulness: {row['faithfulness']:.4f}")
        print(f"  Ctx Precision:{row['context_precision']:.4f}")
        print(f"  Mode        : {row['eval_mode']}")
        print()

    print("-" * 90)
    print("Aggregate metrics (mean across all questions):")
    for key in metric_keys:
        values = [r[key] for r in rows]
        mean = statistics.mean(values)
        min_v = min(values)
        max_v = max(values)
        print(f"  {key:<22} mean={mean:.4f}  min={min_v:.4f}  max={max_v:.4f}")

    if output_json:
        output_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nPer-question results written to {output_json}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-evaluate NASA RAG system against evaluation_dataset.txt")
    parser.add_argument("--eval-file", default="evaluation_dataset.txt", help="Path to evaluation_dataset.txt")
    parser.add_argument("--top-k", type=int, default=4, help="Number of retrieved chunks per question")
    parser.add_argument("--mission", default=None, help="Restrict retrieval to a mission (apollo11/apollo13/challenger)")
    parser.add_argument("--output-json", default=None, help="Optional path to write per-question results as JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    eval_path = Path(args.eval_file)
    if not eval_path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {eval_path}")

    output = Path(args.output_json) if args.output_json else None
    run_batch(eval_path=eval_path, top_k=args.top_k, mission=args.mission, output_json=output)


if __name__ == "__main__":
    main()
