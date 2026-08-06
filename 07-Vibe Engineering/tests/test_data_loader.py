"""Tests for JSON loading and schema validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from flashcard_quizzer.data_loader import FlashcardLoader
from flashcard_quizzer.errors import DataValidationError


def test_load_valid_file(tmp_path: Path) -> None:
    data_file = tmp_path / "cards.json"
    data_file.write_text(
        '[{"Front": "CPU", "Back": "Central Processing Unit"}]',
        encoding="utf-8",
    )

    cards = FlashcardLoader().load_from_file(data_file)

    assert len(cards) == 1
    assert cards[0].front == "CPU"


def test_missing_file_raises_helpful_error(tmp_path: Path) -> None:
    with pytest.raises(DataValidationError, match="Flashcard file not found"):
        FlashcardLoader().load_from_file(tmp_path / "missing.json")


def test_malformed_json_raises_helpful_error(tmp_path: Path) -> None:
    data_file = tmp_path / "broken.json"
    data_file.write_text('{"Front": "CPU"', encoding="utf-8")

    with pytest.raises(DataValidationError, match="Invalid JSON"):
        FlashcardLoader().load_from_file(data_file)


def test_invalid_schema_raises_helpful_error(tmp_path: Path) -> None:
    data_file = tmp_path / "bad_schema.json"
    data_file.write_text('[{"Front": "CPU"}]', encoding="utf-8")

    with pytest.raises(DataValidationError, match="'Back' must be a non-empty string"):
        FlashcardLoader().load_from_file(data_file)
