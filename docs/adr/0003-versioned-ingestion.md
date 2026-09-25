# 0003. Versioned snapshots, deterministic chunk ids

Status: accepted, 2026-09-24

## Context
The original id scheme (a bare positional index) would silently renumber chunks
on every re-run, breaking any citation that outlived the run that produced it.
Source documents can also be replaced at the same URL without notice.

## Decision
Chunk id = hash of document id plus start offset. Each run writes a new snapshot
folder and collection; `current.json` names the live one. Source files are
recorded with SHA256, size and download date. Unchanged documents are skipped.
Manifests and run reports are kept indefinitely; chunk payloads keep the last
KEEP_LAST_N snapshots plus any snapshot pinned by a published result.

## Consequences
Citations survive re-runs. Rollback is a pointer change, not a reprocessing run.
A changed source document is detected instead of silently altering results.
Cost: more disk, and a pointer that must be updated as part of every release.
