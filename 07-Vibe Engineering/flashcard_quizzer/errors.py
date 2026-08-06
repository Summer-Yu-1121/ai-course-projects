"""Custom exception types for the Flashcard Quizzer."""


class FlashcardQuizzerError(Exception):
    """Base application error for user-facing failures."""


class DataValidationError(FlashcardQuizzerError):
    """Raised when flashcard input data is missing or malformed."""
