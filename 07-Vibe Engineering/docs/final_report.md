# AI-Assisted Development Project Report

**Student Name:** Yu Zhang  
**Project Title:** Flashcard Quizzer: AI-Assisted CLI Learning Application  
**Date:** 2026-05-11

## Executive Summary

This project delivers a production-ready Command Line Interface (CLI) application called Flashcard Quizzer. The application loads flashcards from JSON, validates input data robustly, and runs interactive quiz sessions in three modes: sequential, random, and adaptive. It provides immediate feedback after each answer and a complete summary at the end of each session, including total questions, accuracy percentage, and missed terms.

The project was developed using an AI-assisted engineering workflow rather than manual coding from scratch. AI support was used for scaffolding modules, generating tests, and drafting documentation. Each AI-generated output was reviewed against rubric requirements and corrected when needed, especially in validation strictness, adaptive-mode behavior, and static type safety.

The final solution satisfies the core requirements of modular architecture, design pattern usage, type hints, graceful error handling, and test coverage above 80%. The result is a maintainable foundation that can be extended later with additional quiz strategies such as spaced repetition.

## Project Overview

### Problem Statement

New team members often need a lightweight way to memorize domain-specific acronyms and terminology. The requested solution was a terminal tool that could load terms from JSON and run interactive quizzes in multiple modes, while remaining clean and extensible for future growth.

### Solution Approach

The project was implemented with clear separation of concerns:

- `main.py` handles CLI argument parsing and application orchestration.
- `data_loader.py` handles file loading and strict JSON schema validation.
- `strategies.py` encapsulates quiz mode algorithms via the Strategy Pattern.
- `quiz_engine.py` manages quiz-session execution and scoring logic.
- `ui.py` isolates terminal interaction.
- `models.py` defines typed data structures (`Flashcard`, `QuizResult`).
- `errors.py` defines custom exceptions for user-facing failures.

This design supports maintainability and easier refactoring. For example, adding a new mode requires a new strategy class without changing the core engine.

### Final Features

- [x] Load flashcards from JSON file
- [x] Validate malformed/missing file and schema errors with helpful messages
- [x] Sequential, random, and adaptive quiz modes
- [x] Case-insensitive answer checking with immediate feedback
- [x] End-of-session summary with totals, accuracy, and missed terms

## AI Collaboration Experience

### AI Tools Used

- [x] GitHub Copilot
- [ ] Claude
- [ ] ChatGPT
- [ ] Other

### Collaboration Workflow

1. Requirements were decomposed into modules and acceptance checkpoints.
2. AI was asked to generate first-pass code per module.
3. Generated code was reviewed manually against rubric criteria.
4. Problematic suggestions were modified or rejected.
5. Tests, type checks, and runtime commands validated implementation quality.

### Most Valuable AI Interactions

#### Example 1: Architecture Decomposition
**Context:** Needed to transform starter CRUD project into a quiz-focused CLI app.  
**AI Prompt:** "Propose a modular architecture for the Flashcard Quizzer with separation of concerns."  
**AI Response:** Suggested dedicated loader, strategy, engine, and UI modules.  
**Your Changes:** Added custom error hierarchy for graceful command-line failures.  
**Outcome:** Clear structure that maps directly to requirements.

#### Example 2: JSON Validation
**Context:** Rubric required robust data ingestion error handling.  
**AI Prompt:** "Generate a strict JSON loader for flashcards with helpful errors."  
**AI Response:** Basic validation and parsing logic.  
**Your Changes:** Enforced non-empty list and non-empty `Front`/`Back` string constraints.  
**Outcome:** Reliable ingestion with explicit user-facing failures.

#### Example 3: Type Safety Fixes
**Context:** `mypy` failed due to test doubles not matching concrete UI class type.  
**AI Prompt:** "Refactor typing to support fake UI classes cleanly."  
**AI Response:** Introduced protocol-based interface typing.  
**Your Changes:** Applied protocol to both `QuizEngine` and CLI runner signatures.  
**Outcome:** Type checks passed while preserving clean testability.

### Challenges with AI Collaboration

AI-generated code was usually close, but not always production-ready in first pass. Typical issues were:

- Overly permissive validation defaults
- Adaptive mode suggestions that were harder to test deterministically
- Type signatures too concrete for mock/stub testing

The key pattern was that AI accelerated implementation speed, while human review ensured maintainability, determinism, and rubric compliance.

## Software Engineering Practices

### Code Quality Measures

- [x] Code formatting (Black)
- [x] Linting and static checks (`mypy` run)
- [x] Type hints in new modules
- [x] Documentation updates for setup and usage
- [x] Error handling for expected runtime failures

### Testing Strategy

The test suite uses `pytest` and includes both happy paths and error paths:

- Loader tests for valid files, missing files, malformed JSON, and schema failures
- Strategy tests for ordering behavior in all modes
- Engine tests for case-insensitive matching and summary statistics
- CLI tests for graceful error exits and successful session runs

Coverage is above required threshold: **93% total**.

### Design Patterns Used

- **Strategy Pattern:** Implemented in `strategies.py` with `QuizModeStrategy`, `SequentialStrategy`, `RandomStrategy`, and `AdaptiveStrategy`.
- This pattern was selected because quiz mode selection is an algorithmic variation point. It enables future extension (e.g., spaced repetition) without rewriting engine code.

### Code Structure and Organization

The app moved from a starter monolith-style demo into focused modules with single responsibilities. Main orchestration remains small, and domain logic is testable independently from terminal I/O.

## Technical Challenges and Solutions

### Challenge 1: Graceful Failure Without Stack Traces
**Problem:** JSON ingestion errors should not crash with tracebacks.  
**Solution:** Added custom `DataValidationError` and handled all domain errors in `main.py` with user-friendly stderr output and non-zero exit codes.  
**AI Involvement:** AI generated initial exception scaffolding.  
**Lessons Learned:** Explicit exception boundaries are critical for CLI UX.

### Challenge 2: Type-Compatible Test Doubles
**Problem:** Concrete type coupling (`QuizUI`) caused `mypy` failures for test stubs.  
**Solution:** Introduced `QuizUIProtocol` to define behavioral interface typing.  
**AI Involvement:** AI suggested protocol approach after error review.  
**Lessons Learned:** Protocol typing improves both flexibility and static correctness.

## Code Quality Analysis

### Metrics

- Lines of code (new/updated core + tests): ~400
- Test coverage: 93%
- Number of key modules/classes: 8+ modules, multiple strategy classes
- Static type check status: passing

### Self-Assessment

- **Code Readability:** 5/5 - clear module boundaries and focused function scope.
- **Code Maintainability:** 5/5 - strategy abstraction and protocol typing reduce coupling.
- **Test Quality:** 4/5 - strong unit coverage; could add more CLI interaction edge cases.
- **Documentation:** 5/5 - setup, usage, prompts, and collaboration process are documented.

## Learning Outcomes

### Technical Skills Developed

- Better CLI architecture design with `argparse`
- Stronger JSON schema validation practices
- Strategy Pattern implementation for algorithmic extensibility
- Higher confidence in test-driven refinements and static type checks

### AI Collaboration Skills

- Improved prompt specificity (requirements + constraints + acceptance criteria)
- Better code-review discipline for AI outputs
- Faster iteration by combining generation with deterministic verification
- Practical understanding of where AI helps most (scaffolding/tests) vs where manual review is essential

### Software Engineering Insights

- Separation of concerns improves speed and confidence in later refactoring
- Deterministic logic simplifies testing and maintenance
- Quality gates (`black`, `mypy`, `pytest --cov`) are non-negotiable in AI-assisted workflows

## Reflection

### What Worked Well

The most effective pattern was short, targeted prompts plus immediate automated validation. The architecture-first approach avoided many downstream rewrites. Strategy Pattern provided real value and was not merely decorative.

### What Could Be Improved

If time allowed, I would add richer adaptive behavior across persisted sessions and stronger CLI UX options (difficulty tags, category filters, or retries on missed terms).

### Future Enhancements

- Add spaced repetition strategy
- Persist historical miss counts between sessions
- Support CSV import/export
- Add configurable scoring rules and timed quizzes

## Conclusion

This project demonstrates practical AI-assisted software engineering: AI accelerated implementation, while human review ensured correctness, reliability, and maintainability. The final Flashcard Quizzer satisfies the functional and technical rubric requirements, exceeds the coverage threshold, and includes complete submission documentation. The workflow reinforced a key professional lesson: AI can draft quickly, but quality comes from disciplined verification and thoughtful architecture decisions.

## Appendices

### Appendix A: AI Interaction Log

See `docs/ai_edit_log.md` for detailed interaction records and decision rationale.

### Appendix B: Code Statistics

Validated locally with:
- `pytest --cov=. --cov-report=term-missing`
- `mypy .`
- `black .`

### Appendix C: Additional Resources

- Python docs for `argparse`
- Pytest and pytest-cov documentation
- Strategy Pattern reference material from course docs

