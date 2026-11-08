# Verification

## Participant readiness, before new repairs

From starter's activated environment:

```bash
python scripts/verify_workshop.py
```

Requires all inherited Session 2 tests/controls, RAG basics/interface/vector tests, original MCP/NeMo health checks, and the RAG baseline checker. New security tests are intentionally excluded until their exercise. The baseline health check must reproduce cross-owner retrieval and missing retrieval protection; that success does not mean the starter is secure.

## Completed repairs / instructor answer key

```bash
python scripts/verify_workshop.py --secured
python scripts/evaluate_rag.py
```

The answer key defaults to secured expectations even without the flag. The full test suite checks inherited behavior and all RAG repairs. `rag_healthcheck` uses actual Chroma, the stdio MCP SDK connection and the real NeMo worker with explicit Demo model fixtures. `evaluate_rag` measures a labeled context-boundary fixture and reports limitations, not an overall model safety score.

## Live model checks

```bash
python scripts/verify_workshop.py --secured --semantic
```

Also requires real Ollama embeddings, Qwen-generated supported excerpts, and inherited model-based NeMo checks. Optional Gemini requires separate configured credentials and browser observations; it is never assumed tested by a Qwen run.

## Focused repair checks

- Exercise 4–5: `python manage.py test tests.test_rag_access tests.test_rag_provenance`
- Exercise 6: `python manage.py test tests.test_rag_runtime`
- Exercise 7: `python manage.py test tests.test_rag_grounding`
- Isolation/interface: `python manage.py test tests.test_rag_interface`
- Real process retrieval: `python scripts/rag_healthcheck.py --secured`
- Live retrieval/generation: `python scripts/rag_healthcheck.py --secured --live`

No service failure counts as a policy block. Focused unit tests replace some dependencies to test a single rule; real-process health checks provide separate integration evidence. CI runs deterministic checks on Ubuntu with Python 3.13. Inspect its result after push; local results do not prove CI ran.

Chroma operations run in short-lived serialized workers so embedded-engine handles are released between processes on Windows and Linux. Disposable check directories use best-effort cleanup; application indexes remain separately persisted. Never delete a student's database or index to troubleshoot an unrelated test failure.
