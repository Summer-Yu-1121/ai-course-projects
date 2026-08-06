"""Tests for quiz loop behavior and summary statistics."""

from __future__ import annotations

from flashcard_quizzer.models import Flashcard
from flashcard_quizzer.quiz_engine import QuizEngine
from flashcard_quizzer.strategies import SequentialStrategy


class FakeUI:
    """Simple in-memory UI fake for deterministic testing."""

    def __init__(self, answers: list[str]) -> None:
        self._answers = answers
        self.feedback: list[bool] = []
        self.summary = None

    def show_welcome(self, mode_name: str, total_cards: int) -> None:
        self.mode_name = mode_name
        self.total_cards = total_cards

    def ask_question(self, term: str) -> str:
        return self._answers.pop(0)

    def show_feedback(self, is_correct: bool, expected_answer: str) -> None:
        self.feedback.append(is_correct)

    def show_summary(self, result) -> None:
        self.summary = result


def test_quiz_engine_case_insensitive_answers_and_stats() -> None:
    ui = FakeUI(answers=["application programming interface", "wrong answer"])
    cards = [
        Flashcard(front="API", back="Application Programming Interface"),
        Flashcard(front="CLI", back="Command Line Interface"),
    ]

    result = QuizEngine(cards=cards, strategy=SequentialStrategy(), ui=ui).run()

    assert ui.feedback == [True, False]
    assert result.total_questions == 2
    assert result.correct_answers == 1
    assert result.missed_terms == ["CLI"]
    assert result.accuracy_percent == 50.0
