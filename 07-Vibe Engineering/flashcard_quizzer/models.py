"""Domain models for quiz data and results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Flashcard:
    """A single flashcard with prompt and expected answer."""

    front: str
    back: str


@dataclass(frozen=True)
class QuizResult:
    """Aggregate result statistics for one quiz session."""

    total_questions: int
    correct_answers: int
    missed_terms: list[str]

    @property
    def accuracy_percent(self) -> float:
        """Return session accuracy in percentage points."""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
