# GitHub Copilot Instructions – Sudoku Flask Project

## Project Overview
This project is a Python Flask-based Sudoku game.
The goal is to refactor legacy code into a clean, readable, and maintainable application
while adding new features such as difficulty selection, a timer, hints, validation feedback,
dark mode, and a top 10 leaderboard.

GitHub Copilot is used as a development assistant to help with code refactoring,
feature implementation, test setup, and design discussions.

---

## Code Style & Structure Guidelines
- Write clear, readable, and maintainable Python code.
- Follow Python naming conventions (snake_case for variables and functions).
- Prefer small, single-responsibility functions over large functions.
- Organize logic into reusable and testable components.
- Add docstrings and inline comments when logic is not obvious.
- Avoid unnecessary complexity and deeply nested conditionals.

---

## Flask & Technical Constraints
- Use Flask as the web framework.
- Avoid introducing unnecessary frameworks or dependencies.
- Maintain compatibility with the existing starter project where reasonable.
- Keep application state explicit and easy to reason about.
- Avoid global mutable state unless clearly justified.

---

## Game Logic Requirements
- Sudoku puzzles must always have exactly one unique solution.
- Difficulty levels (Easy, Medium, Hard) should control the number of prefilled cells.
- Prefilled cells must be locked and not editable.
- Invalid inputs should trigger immediate visual feedback.
- The game should show a clear completion message when solved correctly.
- Hint functionality should reveal one correct cell and lock it.
- A timer should track how long the player takes to complete the puzzle.
- A Top 10 leaderboard should persist data between sessions.

---

## Testing Expectations
- Prefer testable and modular logic.
- Use pytest for unit testing unless otherwise justified.
- Existing functionality should not break during refactoring.
- Suggest tests when adding major features, and explain what they validate.

---

## How Copilot Should Assist
- Start with high-level explanations before generating large blocks of code.
- Explain design decisions and trade-offs.
- Provide multiple approaches when appropriate.
- Ask for clarification if requirements are ambiguous.
- Avoid modifying unrelated parts of the code unless requested.

---

## Working Style Preferences
- Address larger architectural changes before small tweaks.
- Approve or reject suggestions step by step.
- Keep each Copilot chat focused on one task.
- Favor clarity and maintainability over clever or overly complex solutions.