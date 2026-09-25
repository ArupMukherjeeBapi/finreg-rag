# 0002. Modular monolith, not microservices

Status: accepted, 2026-09-24

## Context
One document, one user, a demo. Separate services would add deployment,
networking and debugging work without a load that justifies it.

## Decision
One application with internal modules (ingestion, index, retrieval, generation,
llm, api, core) and one-way dependencies. Nothing depends on `api`.

## Consequences
Every module runs from a script or a test without a web server. Extracting a
module into its own service later means adding an HTTP layer around it, not
rewriting it. Trigger for that split: one module needing to scale or deploy
independently of the rest.
