# NASA Mission RAG Chat System

End-to-end Retrieval-Augmented Generation (RAG) project for questions about NASA missions (Apollo 11, Apollo 13, Challenger).

## Project Files

- `embedding_pipeline.py`: Chunks mission text files, creates OpenAI embeddings, stores in ChromaDB.
- `rag_client.py`: Runs semantic retrieval from ChromaDB and formats context.
- `llm_client.py`: Calls OpenAI chat models with NASA expert system prompt and conversation history.
- `ragas_evaluator.py`: Evaluates response quality with RAGAS (falls back to heuristic mode if unavailable).
- `chat.py`: Streamlit chat UI that combines retrieval, generation, and evaluation.
- `evaluation_dataset.txt`: Sample evaluation questions with expected answer intents.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your API key:

```bash
export OPENAI_API_KEY="your_key_here"
```

## Build Embeddings

```bash
python embedding_pipeline.py --update-mode replace
```

The command reads mission `.txt` files from `data/raw/` and writes a ChromaDB index to `db/chroma/`.

### Full CLI reference

| Flag | Default | Description |
|---|---|---|
| `--raw-data-dir` | `data/raw` | Directory containing `.txt` source files |
| `--chroma-dir` | `db/chroma` | Persistent ChromaDB directory |
| `--collection-name` | `nasa_missions` | ChromaDB collection name |
| `--embedding-model` | `text-embedding-3-small` | OpenAI embedding model |
| `--chunk-size` | `900` | Max characters per chunk |
| `--chunk-overlap` | `150` | Overlap between consecutive chunks |
| `--batch-size` | `64` | Embedding API batch size |
| `--update-mode` | `update` | `skip` (ignore existing IDs) / `update` (upsert all) / `replace` (drop + re-embed) |
| `--stats-only` | off | Print collection size and per-mission chunk counts, then exit |

Examples:

```bash
# First-time build
python embedding_pipeline.py --update-mode replace

# Inspect existing collection without re-indexing
python embedding_pipeline.py --stats-only

# Add new documents without touching already-indexed chunks
python embedding_pipeline.py --update-mode skip
```

## Run Chat App

```bash
streamlit run chat.py
```

## Batch Evaluation

Run all questions in `evaluation_dataset.txt` end-to-end and print per-question metrics and aggregates:

```bash
python run_batch_eval.py
# Optional flags:
python run_batch_eval.py --top-k 6 --mission apollo13 --output-json results.json
```

## Notes

- Add real mission transcripts and technical documents into `data/raw/`.
- The evaluator uses true RAGAS metrics when available; otherwise it returns heuristic scores.

