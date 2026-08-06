"""Build a ChromaDB index from NASA mission text files."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import chromadb
from openai import OpenAI


@dataclass(frozen=True)
class PipelineConfig:
    raw_data_dir: Path = Path("data/raw")
    chroma_path: Path = Path("db/chroma")
    collection_name: str = "nasa_missions"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 900
    chunk_overlap: int = 150
    batch_size: int = 64


class EmbeddingPipeline:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.openai = OpenAI(api_key=api_key)
        self.chroma_client = chromadb.PersistentClient(path=str(self.config.chroma_path))
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def discover_documents(self) -> list[Path]:
        return sorted(self.config.raw_data_dir.rglob("*.txt"))

    def read_document(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore").strip()

    def split_text(self, text: str) -> list[str]:
        if not text:
            return []

        words = text.split()
        if not words:
            return []

        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for word in words:
            extra = len(word) + (1 if current else 0)
            if current and current_len + extra > self.config.chunk_size:
                chunk = " ".join(current)
                chunks.append(chunk)

                if self.config.chunk_overlap > 0:
                    overlap_words: list[str] = []
                    overlap_len = 0
                    for existing in reversed(current):
                        extra_existing = len(existing) + (1 if overlap_words else 0)
                        if overlap_len + extra_existing > self.config.chunk_overlap:
                            break
                        overlap_words.append(existing)
                        overlap_len += extra_existing
                    current = list(reversed(overlap_words))
                    current_len = sum(len(w) for w in current) + max(0, len(current) - 1)
                else:
                    current = []
                    current_len = 0

            if current:
                current_len += 1
            current.append(word)
            current_len += len(word)

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.openai.embeddings.create(model=self.config.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def _mission_from_path(self, path: Path) -> str:
        stem = path.stem.lower()
        if "apollo11" in stem or "apollo_11" in stem or "apollo-11" in stem:
            return "apollo11"
        if "apollo13" in stem or "apollo_13" in stem or "apollo-13" in stem:
            return "apollo13"
        if "challenger" in stem:
            return "challenger"
        return "unknown"

    def _iter_batches(self, items: list[dict]) -> Iterable[list[dict]]:
        size = self.config.batch_size
        for i in range(0, len(items), size):
            yield items[i : i + size]

    def print_stats(self) -> None:
        count = self.collection.count()
        metas = self.collection.get(include=["metadatas"])["metadatas"]
        by_mission: dict[str, int] = {}
        for m in metas:
            key = (m or {}).get("mission", "unknown")
            by_mission[key] = by_mission.get(key, 0) + 1
        print(f"Collection : {self.config.collection_name}")
        print(f"Total chunks: {count}")
        for k, v in sorted(by_mission.items()):
            print(f"  {k}: {v} chunks")

    def build_index(self, update_mode: str = "update") -> int:
        """Index documents.

        update_mode:
          replace – drop and recreate the collection, then embed everything.
          update  – upsert all chunks (overwrites if ID already exists).
          skip    – only embed chunks whose ID is not already in the collection.
        """
        if update_mode == "replace":
            try:
                self.chroma_client.delete_collection(self.config.collection_name)
            except Exception:
                pass
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.config.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

        documents = self.discover_documents()
        if not documents:
            raise FileNotFoundError(f"No .txt files found in {self.config.raw_data_dir}")

        all_records: list[dict] = []
        for path in documents:
            text = self.read_document(path)
            chunks = self.split_text(text)
            mission = self._mission_from_path(path)
            for i, chunk in enumerate(chunks):
                all_records.append(
                    {
                        "id": f"{path.stem}-{i}",
                        "text": chunk,
                        "metadata": {
                            "mission": mission,
                            "source": str(path),
                            "chunk": i,
                        },
                    }
                )

        if not all_records:
            return 0

        if update_mode == "skip":
            existing_ids = set(
                self.collection.get(ids=[r["id"] for r in all_records])["ids"]
            )
            all_records = [r for r in all_records if r["id"] not in existing_ids]
            if not all_records:
                print("All chunks already indexed — nothing to do (skip mode).")
                return 0

        for batch in self._iter_batches(all_records):
            texts = [x["text"] for x in batch]
            embeddings = self._embed_batch(texts)
            self.collection.upsert(
                ids=[x["id"] for x in batch],
                documents=texts,
                metadatas=[x["metadata"] for x in batch],
                embeddings=embeddings,
            )

        return len(all_records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build embeddings for NASA mission text files.")
    parser.add_argument("--raw-data-dir", default="data/raw", help="Directory containing .txt files")
    parser.add_argument("--chroma-dir", default="db/chroma", help="Persistent ChromaDB path")
    parser.add_argument("--collection-name", default="nasa_missions", help="Collection name")
    parser.add_argument("--embedding-model", default="text-embedding-3-small")
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument(
        "--update-mode",
        choices=["skip", "update", "replace"],
        default="update",
        help="How to handle already-indexed documents: "
             "skip = ignore existing IDs, "
             "update = upsert all (default), "
             "replace = drop collection and re-embed everything",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Print collection size and per-mission chunk counts, then exit",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = PipelineConfig(
        raw_data_dir=Path(args.raw_data_dir),
        chroma_path=Path(args.chroma_dir),
        collection_name=args.collection_name,
        embedding_model=args.embedding_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        batch_size=args.batch_size,
    )
    pipeline = EmbeddingPipeline(config)

    if args.stats_only:
        pipeline.print_stats()
        return

    count = pipeline.build_index(update_mode=args.update_mode)
    print(f"Indexed {count} chunks into collection '{config.collection_name}'.")


if __name__ == "__main__":
    main()
