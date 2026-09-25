# 0001. All model calls go through one module

Status: accepted, 2026-09-20

## Context
Model providers differ in SDK, limits and hosting location. During M1 the first
provider returned capacity errors and had to be replaced mid-build.

## Decision
Every model call goes through `llm.py`, which exposes `ask_llm(prompt) -> str`.
No other module imports a provider SDK.

## Consequences
Switching provider touched one file (Gemini to Mistral, M1). Retries, timeouts,
fallback and cost logging have one place to live. The cost is a thin layer that
hides provider-specific features until they are added deliberately.
