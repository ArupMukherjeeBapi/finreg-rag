# finreg-rag

Cited Q&A assistant over public financial-regulation documents (RAG).
Work in progress, built in public.

## Status

M2 done (ingestion, 47 pages into 140 chunks with page metadata). M3 in progress.
Full roadmap and milestone definitions: [docs/architecture.md](docs/architecture.md#roadmap)

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


## Known limitations
- Chunk `start` offsets are recorded before whitespace stripping, so they are
  approximate. Sufficient for page-level citation, not for exact passage highlighting.
- PDF page numbers differ from the printed page numbers (cover and contents pages).
  Citations refer to PDF pages.
- Repeated page headers are not stripped yet; impact on retrieval will be measured first.
- PDF text extraction produces occasional broken words ("JS Ts" for "JSTs",
  "conducte d" for "conducted"). Characters are positioned in a PDF, not stored
  as words. This affects every retrieval method equally and will be measured in
  M4 before any repair is attempted.







