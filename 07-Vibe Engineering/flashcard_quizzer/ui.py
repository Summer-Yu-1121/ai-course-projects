"""Terminal user interface for the quiz experience."""

from __future__ import annotations

from typing import Protocol

from flashcard_quizzer.models import QuizResult


class QuizUIProtocol(Protocol):
    """Protocol for quiz I/O to enable test doubles and alternate UIs."""

    def show_welcome(self, mode_name: str, total_cards: int) -> None:
        """Display intro details."""

    def ask_question(self, term: str) -> str:
        """Prompt and return user answer."""

    def show_feedback(self, is_correct: bool, expected_answer: str) -> None:
        """Display per-question feedback."""

    def show_summary(self, result: QuizResult) -> None:
        """Display end-of-session summary."""


class QuizUI:
    """Simple text-based input/output adapter."""

    def show_welcome(self, mode_name: str, total_cards: int) -> None:
        """Print session intro details."""
        print("Flashcard Quizzer")
        print("=" * 40)
        print(f"Mode: {mode_name}")
        print(f"Cards loaded: {total_cards}\n")

    def ask_question(self, term: str) -> str:
        """Prompt the user for an answer and return normalized text."""
        return input(f"Q: {term}\nA: ").strip()

    def show_feedback(self, is_correct: bool, expected_answer: str) -> None:
        """Show immediate correctness feedback."""
        if is_correct:
            print("Correct.\n")
        else:
            print(f"Incorrect. Correct answer: {expected_answer}\n")

    def show_summary(self, result: QuizResult) -> None:
        """Print end-of-session statistics."""
        print("Session Summary")
        print("-" * 40)
        print(f"Total Questions : {result.total_questions}")
        print(f"Accuracy %      : {result.accuracy_percent:.2f}")
        missed_display = (
            ", ".join(result.missed_terms) if result.missed_terms else "None"
        )
        print(f"Missed Terms    : {missed_display}")
