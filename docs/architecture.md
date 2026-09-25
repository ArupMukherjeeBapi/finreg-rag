# Architecture

Status: in progress. Sections marked **planned** are designed but not yet built.
Last updated: 2026-09-25

## What this system does

Answers questions about public financial-regulation documents, and cites the exact
document, version and page for every answer. If no source covers the question, it
says so instead of guessing. In a regulated domain an unsourced answer is unusable.

## Shape: modular monolith

One deployable application, divided into modules with one-way dependencies.
Each module is reachable only through a defined interface, so any of them can be
replaced or later extracted into its own service without touching its callers.

Offline path (ingestion job):

    ingestion ──> index        writes a new snapshot
    ingestion ──> llm          embeddings for the vector index

Online path (request):

    api ──> generation ──> retrieval ──> index
                  └──────> llm

All modules depend on `core` (shared types and errors).

Rule: dependencies point downward only. `index` must never import `api`.
Reason: lower modules must stay usable from a CLI, a test, or a future separate
service, without dragging the web layer and its configuration in with them.

## Two paths through the system

**Ingestion (offline, no user waiting):**

    PDF -> extract text (per page) -> chunk (+ page number)
        -> write snapshot (SQLite + Qdrant collection) -> update pointer

**Serving (online, user waiting):**

    question -> retrieve top-k chunks (hybrid) -> build prompt (question + chunks)
             -> LLM -> answer + citations -> response

## Modules

| Module | Responsibility | Fails how |
|---|---|---|
| `ingestion` | PDF to chunks with page metadata | Job fails, previous snapshot stays live |
| `index` | Stores chunks, keyword and vector lookup | Vector store down: keyword only (degraded) |
| `retrieval` | Question to best chunks (hybrid scoring) | Returns an empty result; never invents or substitutes chunks |
| `generation` | Chunks plus question to cited answer | Provider down: retry, then fallback provider |
| `llm` | One door to any LLM provider | Retries, timeouts, fallback live here |
| `api` | HTTP: validation, errors, logging, idempotency, health endpoint reporting index and vector store availability | Returns typed errors, never a stack trace; answers carry a flag when results came from keyword only (degraded) |
| `core` | Shared types (Chunk, Answer) and error classes | - |

## Storage

| Data | Where | Role |
|---|---|---|
| Chunk text, page, document id, version | SQLite | Source of truth |
| Keyword index (BM25) | SQLite FTS5 | Exact terms: "Article 6(4)", "SREP" |
| Vectors | Qdrant (Cloud free tier) | Meaning: "big banks" ~ "significant institutions" |

Qdrant is a **derived** index, never the source of truth. It can be deleted and
rebuilt from SQLite. This is what makes running without it (degraded mode) safe.

## Versioning and rollback

Each ingestion run writes a new snapshot and does not touch the live one:

    data/processed/v_<timestamp>_<hash>/chunks.db      (SQLite)
    Qdrant collection: finreg_v_<timestamp>_<hash>
    data/processed/current.json -> {"version": "v_<timestamp>_<hash>"}

Rollback is a pointer change, not a re-run. A pointer file is used rather than a
symlink because symlinks on Windows require administrator rights.

Idempotency: chunk id = sha256(document_id + ":" + start_offset), truncated.
The same document at the same position always produces the same id, so citations
stay valid across re-runs. A document whose SHA256 is unchanged is skipped.

Retention: manifests and run reports are kept forever (audit trail, kilobytes).
Chunk payloads keep the last N snapshots (`KEEP_LAST_N`, 0 means keep all), plus
any snapshot pinned by a published eval result or demo.

Until M3.6 the index is written to a single flat `data/processed/index.db`, which
is overwritten on every build. Versioning lands once the snapshot also has to
contain the vector collection, so it is built once rather than twice.

## Trust boundaries

Document text is **untrusted input**. A PDF can contain "ignore previous
instructions". Document content is passed to the model as clearly delimited
reference material, never as instructions, and every claim must carry a citation.
**planned**

## Roadmap

| Milestone | Delivers | Status |
|---|---|---|
| M0-M2 | Repo, provider-agnostic LLM call, ingestion with page metadata | done |
| M3.1 | Keyword baseline retrieval (measuring stick, in memory) | done |
| M3.2 | Chunks in SQLite, keyword search with FTS5 and BM25 ranking | done |
| M3.3 | Embeddings stored in Qdrant | next |
| M3.4 | Hybrid retrieval: keyword and vector scores combined | planned |
| M3.5 | Cited answers, refusal when no source is relevant | planned |
| M3.6 | Versioned snapshot for the whole index (SQLite file plus Qdrant collection) and `current.json` pointer, per ADR 0003 | planned |
| M4 | Evaluation set, accuracy, cost and latency numbers | planned |
| M5 | FastAPI endpoint, validation, timeouts, retries, logging, health endpoint and degraded-mode flag | planned |
| M6 | CI with an accuracy gate, container build | planned |
| M7 | Multi-step retrieval agent (LangGraph): search, judge, search again | planned |
| Deploy | Public demo, Qdrant Cloud free tier | after M7 |

The core pipeline is hand written so it can be debugged and measured line by
line. LangGraph is used only in M7, where a loop with state and checkpoints
is what the problem actually needs.

## Deliberately out of scope, and what would change that

| Not built | Would build it when |
|---|---|
| Kubernetes | More than one service needs independent scaling |
| Authentication, multi-tenancy | More than one user, or non-public documents |
| Rate-limiting service | Sustained traffic beyond one process |
| Streaming responses | Answers get long enough that latency is felt |
| Reranking model | Evals show retrieval, not generation, is the bottleneck |

## Open questions

Still to be decided in the next design pass:

- Embedding model and vector dimensions
- Hybrid score combination: weighted sum or reciprocal rank fusion
- Refusal threshold: how weak the best-matching chunk must be before the
  system answers "no source covers this"
