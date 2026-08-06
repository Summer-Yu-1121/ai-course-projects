"""Tests for CLI runner behavior and error handling."""

from __future__ import annotations

from pathlib import Path

from main import run


class StubUI:
    """Deterministic UI stub used for integration-style CLI testing."""

    def __init__(self, answers: list[str]) -> None:
        self._answers = answers
        self.summary = None

    def show_welcome(self, mode_name: str, total_cards: int) -> None:
        self.mode_name = mode_name
        self.total_cards = total_cards

    def ask_question(self, term: str) -> str:
        return self._answers.pop(0)

    def show_feedback(self, is_correct: bool, expected_answer: str) -> None:
        self.last_feedback = is_correct

    def show_summary(self, result) -> None:
        self.summary = result


def test_run_returns_1_when_input_file_missing(capsys) -> None:
    code = run(["--file", "does-not-exist.json"])
    captured = capsys.readouterr()

    assert code == 1
    assert "Error:" in captured.err


def test_run_returns_0_for_valid_session(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary.json"
    glossary.write_text(
        '[{"Front": "API", "Back": "Application Programming Interface"}]',
        encoding="utf-8",
    )

    ui = StubUI(answers=["Application Programming Interface"])
    code = run(["--mode", "sequential", "--file", str(glossary)], ui=ui)

    assert code == 0
    assert ui.summary is not None
    assert ui.summary.correct_answers == 1
