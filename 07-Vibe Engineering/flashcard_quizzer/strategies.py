"""Quiz mode strategy implementations for card ordering."""

from __future__ import annotations

from abc import ABC, abstractmethod
import random

from flashcard_quizzer.models import Flashcard


class QuizModeStrategy(ABC):
    """Strategy interface for deciding quiz order."""

    @abstractmethod
    def select_order(self, cards: list[Flashcard], misses: dict[int, int]) -> list[int]:
        """Return a list of card indices in the order they should be asked."""


class SequentialStrategy(QuizModeStrategy):
    """Ask questions in source-file order."""

    def select_order(self, cards: list[Flashcard], misses: dict[int, int]) -> list[int]:
        return list(range(len(cards)))


class RandomStrategy(QuizModeStrategy):
    """Ask all questions in random order."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def select_order(self, cards: list[Flashcard], misses: dict[int, int]) -> list[int]:
        return self._rng.sample(range(len(cards)), len(cards))


class AdaptiveStrategy(QuizModeStrategy):
    """Prioritize cards with higher previous miss counts."""

    def select_order(self, cards: list[Flashcard], misses: dict[int, int]) -> list[int]:
        indices = list(range(len(cards)))
        return sorted(indices, key=lambda idx: (-misses.get(idx, 0), idx))
