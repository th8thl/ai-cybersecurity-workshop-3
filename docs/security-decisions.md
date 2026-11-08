# Security decisions

- Build both applications from the Session 2 solution; retain its repairs and tests.
- Keep one Django settings list, one main URL dispatcher and app-owned routes/templates.
- Add a dedicated scoped read-only MCP tool rather than grant the model document approval or ticket writes through RAG.
- Keep authoritative text/permissions in SQLite; Chroma holds reference vectors and metadata.
- Use explicit Ollama embeddings and separate model collections. Demo is opt-in and labeled.
- Apply access checks before ranking and revalidate each candidate/MCP source afterward.
- Require exact cited excerpts to make the grounding exercise mechanically verifiable.
- Preserve approved-but-false and harmless-quotation cases to make defense limitations measurable.
- Retain private browser Debug, while persistent telemetry stores IDs/hashes/verdicts.
- Do not perform model training, arbitrary document URL fetching, or public document upload in this lab.
