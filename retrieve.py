import json
import re
from pathlib import Path

CHUNKS_PATH = Path("data/processed/chunks.jsonl")


def load_chunks(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score(query_tokens: set[str], chunk_text: str) -> int:
    return len(query_tokens & tokenize(chunk_text))


def search(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    query_tokens = tokenize(query)
    hits = []
    for chunk in chunks:
        s = score(query_tokens, chunk["text"])
        if s > 0:
            hits.append({"score": s, **chunk})
    hits.sort(key=lambda hit: hit["score"], reverse=True)
    return hits[:top_k]


if __name__ == "__main__":
    chunks = load_chunks(CHUNKS_PATH)
    for hit in search("What are joint supervisory teams?", chunks):
        print(f"[score {hit['score']}] page {hit['page']}: {hit['text'][:200]}...")
