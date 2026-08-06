"""Command-line entry point for the Flashcard Quizzer application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from flashcard_quizzer.data_loader import FlashcardLoader
from flashcard_quizzer.errors import FlashcardQuizzerError
from flashcard_quizzer.quiz_engine import QuizEngine
from flashcard_quizzer.strategies import (
    AdaptiveStrategy,
    QuizModeStrategy,
    RandomStrategy,
    SequentialStrategy,
)
from flashcard_quizzer.ui import QuizUI, QuizUIProtocol


def build_parser() -> argparse.ArgumentParser:
    """Build and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer: practice glossary terms from a JSON file."
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "random", "adaptive"],
        default="sequential",
        help="Quiz order mode.",
    )
    parser.add_argument(
        "--file",
        default="data/glossary.json",
        help="Path to the flashcard JSON file.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible random mode.",
    )
    return parser


def _build_strategy(mode: str, seed: int | None) -> QuizModeStrategy:
    """Create a strategy object from the selected mode."""
    if mode == "sequential":
        return SequentialStrategy()
    if mode == "random":
        return RandomStrategy(seed=seed)
    return AdaptiveStrategy()


def run(argv: Sequence[str] | None = None, ui: QuizUIProtocol | None = None) -> int:
    """Run the quiz application and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    ui_instance = ui or QuizUI()

    try:
        loader = FlashcardLoader()
        cards = loader.load_from_file(Path(args.file))
        strategy = _build_strategy(args.mode, args.seed)

        engine = QuizEngine(cards=cards, strategy=strategy, ui=ui_instance)
        engine.run()
        return 0
    except FlashcardQuizzerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nQuiz cancelled by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(run())
