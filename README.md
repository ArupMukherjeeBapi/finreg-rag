# finreg-rag

Cited Q&A assistant over public financial-regulation documents (RAG).
Work in progress, built in public.

## Status
- [x] M1: LLM call through a single provider-agnostic module (`llm.py`)
- [ ] M2: document ingestion and embeddings
- [ ] M3: retrieval with cited answers
- [ ] M4: evaluation harness with accuracy numbers
- [ ] M5: FastAPI + Docker
- [ ] M6: CI and deployment

## Quickstart (Windows / PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then put your real key in .env
python llm.py
```

## Design decisions
- All LLM calls go through `llm.py`. Swapping provider, adding logging or
  cost tracking is a one-file change, which matters where data residency is regulated.
- Secrets live in `.env`, which is git-ignored. `.env.example` documents the variable names.

## Changed the llm provider
- Provider: Mistral (EU-based), swapped in from Gemini in a single file (`llm.py`)
  after the Gemini free tier returned capacity errors. Keeping every call behind
  `ask_llm()` made the migration a one-file change with no other code touched.
- Planned: retry with backoff plus provider fallback inside `llm.py`.

