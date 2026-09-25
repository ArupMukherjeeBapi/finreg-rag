# 0004. SQLite as source of truth, Qdrant for vectors

Status: accepted, 2026-09-25

## Context
Exact terms ("Article 6(4)", "SREP") are found reliably by keyword search;
paraphrases ("big banks" for "significant institutions") need vectors. At this
corpus size neither store is required for performance.

## Decision
SQLite holds chunk text and metadata and serves keyword search (FTS5). Qdrant
holds vectors only and is treated as a derived index, rebuildable from SQLite.
Retrieval combines both scores. Qdrant Cloud free tier hosts the demo.

## Consequences
Losing the vector store degrades the system to keyword-only rather than breaking
it; that state must be visible in the health check and flagged on the answer.
Honest note: at this corpus size SQLite with in-memory vectors would suffice.
Qdrant is chosen deliberately for the operational experience and the growth path,
and the vector store sits behind an interface so it can be replaced.
