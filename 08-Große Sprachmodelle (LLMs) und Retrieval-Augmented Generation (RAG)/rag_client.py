"""Retrieval client for querying ChromaDB with semantic search."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import chromadb
from openai import OpenAI


@dataclass(frozen=True)
class RAGConfig:
    chroma_path: str = "db/chroma"
    collection_name: str = "nasa_missions"
    embedding_model: str = "text-embedding-3-small"


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    metadata: dict[str, Any]
    distance: float


class RAGClient:
    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.openai = OpenAI(api_key=api_key)
        self.chroma_client = chromadb.PersistentClient(path=self.config.chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(self.config.collection_name)

    def _embed_query(self, question: str) -> list[float]:
        response = self.openai.embeddings.create(
            model=self.config.embedding_model,
            input=question,
        )
        return response.data[0].embedding

    def search(self, question: str, top_k: int = 4, mission: str | None = None) -> list[RetrievedChunk]:
        query_embedding = self._embed_query(question)

        where = None
        if mission and mission.lower() != "all":
            where = {"mission": mission.lower()}

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        chunks: list[RetrievedChunk] = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            chunks.append(RetrievedChunk(text=doc, metadata=meta or {}, distance=float(dist)))
        return chunks

    def format_context(self, chunks: list[RetrievedChunk], max_chars: int = 8000) -> str:
        if not chunks:
            return "No relevant context found in the mission archive."

        parts: list[str] = []
        consumed = 0
        for i, chunk in enumerate(chunks, start=1):
            source = chunk.metadata.get("source", "unknown")
            mission = chunk.metadata.get("mission", "unknown")
            header = f"[Source {i} | mission={mission} | file={source}]\n"
            body = chunk.text.strip()
            block = header + body + "\n"
            if consumed + len(block) > max_chars:
                break
            parts.append(block)
            consumed += len(block)
        return "\n".join(parts)

    def retrieve_context(
        self,
        question: str,
        top_k: int = 4,
        mission: str | None = None,
    ) -> tuple[str, list[RetrievedChunk]]:
        chunks = self.search(question=question, top_k=top_k, mission=mission)
        return self.format_context(chunks), chunks
