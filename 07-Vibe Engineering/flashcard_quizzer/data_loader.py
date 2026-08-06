"""Load and validate flashcards from JSON input."""

from __future__ import annotations

import json
from pathlib import Path

from flashcard_quizzer.errors import DataValidationError
from flashcard_quizzer.models import Flashcard


class FlashcardLoader:
    """Load flashcards from a JSON file with strict schema validation."""

    def load_from_file(self, file_path: Path) -> list[Flashcard]:
        """Read and validate flashcards from the specified path."""
        if not file_path.exists():
            raise DataValidationError(f"Flashcard file not found: {file_path}")

        try:
            raw_data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DataValidationError(
                f"Invalid JSON in file {file_path}: {exc.msg}"
            ) from exc
        except OSError as exc:
            raise DataValidationError(
                f"Unable to read file {file_path}: {exc}"
            ) from exc

        return self._validate_and_build(raw_data, file_path)

    def _validate_and_build(self, raw_data: object, file_path: Path) -> list[Flashcard]:
        if not isinstance(raw_data, list):
            raise DataValidationError(
                f"Invalid data format in {file_path}: top-level JSON must be a list."
            )

        cards: list[Flashcard] = []
        for index, item in enumerate(raw_data, start=1):
            if not isinstance(item, dict):
                raise DataValidationError(
                    f"Invalid card at position {index}: card must be an object."
                )

            front = item.get("Front")
            back = item.get("Back")
            if not isinstance(front, str) or not front.strip():
                raise DataValidationError(
                    f"Invalid card at position {index}: 'Front' must be a non-empty string."
                )
            if not isinstance(back, str) or not back.strip():
                raise DataValidationError(
                    f"Invalid card at position {index}: 'Back' must be a non-empty string."
                )

            cards.append(Flashcard(front=front.strip(), back=back.strip()))

        if not cards:
            raise DataValidationError(
                f"No flashcards found in {file_path}: the list cannot be empty."
            )

        return cards
