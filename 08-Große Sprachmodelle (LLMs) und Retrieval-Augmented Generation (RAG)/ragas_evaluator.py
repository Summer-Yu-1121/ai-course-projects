"""Quality evaluator for RAG responses using RAGAS with a safe fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvaluatorConfig:
    enabled: bool = True


class RagasEvaluator:
    def __init__(self, config: EvaluatorConfig | None = None) -> None:
        self.config = config or EvaluatorConfig()
        self._ragas_available = False
        self._evaluate = None
        self._metrics: dict[str, Any] = {}

        if not self.config.enabled:
            return

        try:
            from ragas import evaluate
            from ragas.metrics import answer_relevancy, faithfulness

            self._evaluate = evaluate
            self._metrics["answer_relevancy"] = answer_relevancy
            self._metrics["faithfulness"] = faithfulness

            try:
                from ragas.metrics import context_precision

                self._metrics["context_precision"] = context_precision
            except Exception:
                pass

            self._ragas_available = True
        except Exception:
            self._ragas_available = False

    @staticmethod
    def _heuristic_scores(question: str, answer: str, contexts: list[str]) -> dict[str, float]:
        question_terms = {x for x in question.lower().split() if len(x) > 3}
        answer_terms = set(answer.lower().split())
        context_terms = set(" ".join(contexts).lower().split()) if contexts else set()

        relevance = 0.0
        if question_terms:
            relevance = len(question_terms & answer_terms) / len(question_terms)

        grounding = 0.0
        if answer_terms:
            grounding = len(answer_terms & context_terms) / len(answer_terms)

        context_util = 0.0
        if context_terms:
            context_util = len(answer_terms & context_terms) / len(context_terms)

        return {
            "answer_relevancy": round(float(min(1.0, relevance)), 4),
            "faithfulness": round(float(min(1.0, grounding)), 4),
            "context_precision": round(float(min(1.0, context_util)), 4),
            "mode": "heuristic",
        }

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        reference: str | None = None,
    ) -> dict[str, Any]:
        if not self._ragas_available or self._evaluate is None:
            return self._heuristic_scores(question, answer, contexts)

        try:
            from datasets import Dataset

            # RAGAS >=0.2 schema
            payload = {
                "user_input": [question],
                "response": [answer],
                "retrieved_contexts": [contexts],
            }
            if reference:
                payload["reference"] = [reference]

            dataset = Dataset.from_dict(payload)
            metrics = [self._metrics["answer_relevancy"], self._metrics["faithfulness"]]
            if reference and "context_precision" in self._metrics:
                metrics.append(self._metrics["context_precision"])

            result = self._evaluate(dataset=dataset, metrics=metrics)
            scores = result.to_pandas().iloc[0].to_dict()
            scores["mode"] = "ragas"
            return {k: float(v) if isinstance(v, (int, float)) else v for k, v in scores.items()}
        except Exception:
            return self._heuristic_scores(question, answer, contexts)
