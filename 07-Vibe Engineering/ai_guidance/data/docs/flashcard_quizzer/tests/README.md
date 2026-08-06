# Flashcard Quizzer (AI-Assisted CLI Application)

Flashcard Quizzer is a production-ready Python CLI app that helps users memorize glossary terms from JSON flashcards.

This project was built using an AI-assisted workflow and includes:
- Robust JSON ingestion and validation
- Three quiz modes powered by the Strategy Pattern
- Case-insensitive answer checking
- Session summary statistics
- Type hints, unit tests, and coverage reports

## Features

1. Data Ingestion and Validation
- Loads cards from a JSON file.
- Requires each item to include non-empty `Front` and `Back` string fields.
- Handles missing/malformed files with user-friendly error messages (no stack trace).

2. Quiz Loop
- Displays the `Front` term.
- Accepts terminal input as the answer.
- Compares answers to `Back` case-insensitively.
- Shows immediate correctness feedback.

3. Quiz Modes (Strategy Pattern)
- `sequential`: asks cards in file order.
- `random`: asks cards in shuffled order.
- `adaptive`: prioritizes cards with higher previous miss counts.

4. Session Stats
- Displays total questions.
- Displays accuracy percentage.
- Displays missed terms.

## Project Structure

```text
starter/
├── main.py
├── data/
│   └── glossary.json
├── flashcard_quizzer/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── errors.py
│   ├── models.py
│   ├── quiz_engine.py
│   ├── strategies.py
│   └── ui.py
├── tests/
│   ├── test_data_loader.py
│   ├── test_main.py
│   ├── test_quiz_engine.py
│   ├── test_strategies.py
│   ├── test_file_handler.py
│   └── test_task_manager.py
├── docs/
│   ├── ai_edit_log.md
│   ├── final_report.md
│   ├── project_rubric.md
│   └── report_template.md
├── prompts.md
└── requirements.txt
```

## Requirements

- Python 3.10+
- pip
- venv

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the Application

Help command:

```bash
python main.py --help
```

Run quiz in sequential mode:

```bash
python main.py --mode sequential --file data/glossary.json
```

Other modes:

```bash
python main.py --mode random --file data/glossary.json
python main.py --mode adaptive --file data/glossary.json
```

Optional random seed:

```bash
python main.py --mode random --file data/glossary.json --seed 42
```

## Quality Checks

Format:

```bash
black .
```

Type check:

```bash
mypy .
```

Test + coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

## Coverage Result

Current test suite achieves over 80% total coverage (project run: 93%).

## Notes on AI Collaboration

- Prompt history is in `prompts.md`.
- Detailed AI interaction review is in `docs/ai_edit_log.md`.
- Final reflection report is in `docs/final_report.md`.

