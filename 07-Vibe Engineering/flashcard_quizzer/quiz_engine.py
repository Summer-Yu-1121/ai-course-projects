"""Quiz execution logic isolated from CLI and storage concerns."""

from __future__ import annotations

from flashcard_quizzer.models import Flashcard, QuizResult
from flashcard_quizzer.strategies import QuizModeStrategy
from flashcard_quizzer.ui import QuizUIProtocol


class QuizEngine:
    """Run quiz sessions using pluggable ordering strategies."""

    def __init__(
        self,
        cards: list[Flashcard],
        strategy: QuizModeStrategy,
        ui: QuizUIProtocol,
    ) -> None:
        self._cards = cards
        self._strategy = strategy
        self._ui = ui

    def run(self) -> QuizResult:
        """Execute one quiz session and return summarized results."""
        misses: dict[int, int] = {}
        missed_terms: list[str] = []
        correct_answers = 0

        self._ui.show_welcome(self._strategy.__class__.__name__, len(self._cards))

        order = self._strategy.select_order(self._cards, misses)
        for idx in order:
            card = self._cards[idx]
            user_answer = self._ui.ask_question(card.front)
            is_correct = user_answer.casefold() == card.back.casefold()

            if is_correct:
                correct_answers += 1
            else:
                misses[idx] = misses.get(idx, 0) + 1
                missed_terms.append(card.front)

            self._ui.show_feedback(is_correct=is_correct, expected_answer=card.back)

        result = QuizResult(
            total_questions=len(self._cards),
            correct_answers=correct_answers,
            missed_terms=missed_terms,
        )
        self._ui.show_summary(result)
        return result
