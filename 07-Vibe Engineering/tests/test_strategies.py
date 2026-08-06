"""Tests for quiz mode strategy ordering behavior."""

from __future__ import annotations

from flashcard_quizzer.models import Flashcard
from flashcard_quizzer.strategies import (
    AdaptiveStrategy,
    RandomStrategy,
    SequentialStrategy,
)


def _cards() -> list[Flashcard]:
    return [
        Flashcard(front="A", back="a"),
        Flashcard(front="B", back="b"),
        Flashcard(front="C", back="c"),
    ]


def test_sequential_strategy_uses_source_order() -> None:
    order = SequentialStrategy().select_order(_cards(), misses={})
    assert order == [0, 1, 2]


def test_random_strategy_shuffles_but_keeps_all_indices() -> None:
    order = RandomStrategy(seed=7).select_order(_cards(), misses={})
    assert sorted(order) == [0, 1, 2]
    assert order != [0, 1, 2]


def test_adaptive_strategy_prioritizes_previously_missed_cards() -> None:
    misses = {0: 1, 2: 3, 1: 1}
    order = AdaptiveStrategy().select_order(_cards(), misses=misses)
    assert order[0] == 2
