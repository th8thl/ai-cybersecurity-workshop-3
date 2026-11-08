# Session 3 — RAG Security, Hallucinations and Runtime Defense

RAG is a key part of building useful business AI: it connects a model to an organization's current knowledge without retraining the model. This workshop extends the **Session 2 solution**, retaining the support portal, ticket application, authentication, delegated MCP grants, ownership checks, human confirmation, NeMo and the existing tests.

The new challenge is the **knowledge the assistant reads**. Students inspect embeddings and semantic search, poison a synthetic knowledge base, and repair document access, provenance, runtime content checks and answer grounding. Document content and MCP results remain untrusted evidence.

## Workshop materials

- [Codespaces setup](docs/GITHUB_CODESPACES_SETUP.md) / [local setup](docs/LOCAL_SETUP.md)
- [Exercises and timings](docs/EXERCISES.md) / [instructor guide](docs/INSTRUCTOR_NOTES.md)
- [Attack cases](docs/ATTACK_PROMPTS.md) / [student evidence](docs/NOTES_TEMPLATE.md)
- [Architecture and threat model](docs/THREAT_MODEL.md)
- [Curriculum coverage](docs/SCOPE_AND_EVIDENCE.md) / [verification](docs/VERIFICATION.md) / [local validation](docs/VALIDATION.md)
- [Offline slides](session3_workshop_deck.html)
- [RAG concepts and framework](docs/RAG_FRAMEWORK.md)

## Distribution pattern

Distribute `starter/`; keep `solution/` as the instructor answer key. Both copies begin with all Session 2 ticket repairs. The starter deliberately omits four **new** RAG controls in `knowledge/controls.py`, uses a weak RAG policy prompt, and has the retrieval NeMo flow disabled. The solution includes the repairs. The tests are identical; security tests intentionally fail in the unchanged starter. There is no environment variable that turns the starter into the solution.

## System architecture

![Django RAG architecture and trust boundaries](docs/system-architecture.svg)

## Project organization

```text
.devcontainer/                 Same Python 3.12 / Ollama / private port setup
.github/workflows/security.yml CI checks both workshop states
docs/                          Student and instructor evidence-driven guides
starter/                       Participant application
solution/                      Instructor answer key
  manage.py
  support_portal/               Django settings, main URLs, theme
  tickets/                      Inherited application and permissions
  chatbot/                      Inherited assistant, consent and MCP client
  knowledge/                    New Django app
    models.py                   Documents, passages, privacy-conscious runtime events
    ingestion.py                Chunking and embedding
    embeddings.py               Ollama embeddings; explicit demo fixture
    vector_store.py             Local persistent Chroma, cosine distance
    vector_worker.py            Serialized, bounded index operations
    retrieval.py                Shared website/MCP search service
    controls.py                 Four focused student repairs
    generation.py               Qwen/Gemini/Demo cited-answer generation
    grounding.py                Exact-excerpt source validation
    pipeline.py                 Runtime checks and telemetry
    corpus/                     Clean and poisoned source PDFs; metadata-only manifest
    management/commands/        Seed, index and embedding-inspection commands
    templates/knowledge/        Portal-consistent knowledge workspace
  mcp_server/server.py          Existing ticket tools plus search_knowledge
  guardrails/                   Existing rails plus retrieval Colang flow
  security/                     Existing delegated grant and redaction controls
  tests/                        Existing tests plus RAG tests
  scripts/                      Setup, tests, real-process checks, evaluation and SAST
```

One Django server contains all three apps. The root URL still opens Tickets. **Assistant** retains ticket actions; **Knowledge** opens the RAG workflow at `/chatbot/knowledge/`, under the existing assistant token cookie path. Ordinary tickets still work without a model, MCP or assistant grant. Knowledge retrieval through the assistant requires the new `knowledge:read` permission.

## Quick start after setup

From the repository root in Codespaces:

```bash
cd starter
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

Sign in, open Authorization, grant **Search my permitted knowledge base** for 30 minutes, then open Knowledge. It starts empty. Follow Exercise 2 to load documents and build the index yourself before asking `How do I recover my account?`. Use **Inspect search only** before **Get answer**. Expand Debug to see dimensions, vector preview, ranked sources, exact prompt and runtime checks.

Default embeddings use `embeddinggemma:300m` through Ollama; Qwen remains the default answer model. Chroma is local, needs no account or separate service, and never chooses an embedding model implicitly. Explicit Demo embeddings and responses are labeled fixtures; they do not establish live-model behavior.

The answer exercise deliberately requires **verbatim cited excerpts**. This makes unsupported text mechanically rejectable. It is not a general semantic fact checker, and an approved source can still be wrong. The lab changes retrieved context, not model weights.

Vector index operations run in a bounded local worker with a cross-process lock. Each worker exits after one Chroma operation, releasing embedded-engine handles before ingestion, Django or MCP opens the same index again. This requires no additional service or port.
