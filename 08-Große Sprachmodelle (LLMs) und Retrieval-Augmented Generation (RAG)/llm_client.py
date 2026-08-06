"""LLM client that answers questions using retrieved context."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from openai import OpenAI


DEFAULT_SYSTEM_PROMPT = (
    "You are a NASA mission operations specialist. "
    "Answer in clear English, be factual, and only use the provided context. "
    "If information is missing, explicitly say what is unknown. "
    "When possible, mention the source identifiers included in context."
)


@dataclass
class LLMConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 600
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


@dataclass
class ConversationTurn:
    role: str
    content: str


@dataclass
class LLMClient:
    config: LLMConfig = field(default_factory=LLMConfig)

    def __post_init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.history: list[ConversationTurn] = []

    def reset_history(self) -> None:
        self.history = []

    def _build_messages(self, question: str, context: str, history_window: int = 8) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": self.config.system_prompt}]

        for turn in self.history[-history_window:]:
            messages.append({"role": turn.role, "content": turn.content})

        user_payload = (
            "Use the context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Return a concise but complete answer and cite sources like [Source 1] when available."
        )
        messages.append({"role": "user", "content": user_payload})
        return messages

    def answer_question(self, question: str, context: str) -> str:
        messages = self._build_messages(question=question, context=context)
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        answer = response.choices[0].message.content or "I could not generate an answer."

        self.history.append(ConversationTurn(role="user", content=question))
        self.history.append(ConversationTurn(role="assistant", content=answer))
        return answer
