# Instructor guide

Session 1 protected user-input/prompt boundaries. Session 2 protected actions with application authorization. Session 3 protects the external knowledge and tool results entering runtime context. Students first inspect working retrieval, then show poisoned content, repair focused controls, and repeat benign and malicious cases.

Allow approximately 180 minutes excluding installation and downloads. The reference answer key and starter share all tests and Session 2 repairs. Never reset a student's environment or database to recreate an attack.

## Prepare

Use a fresh starter copy. Complete environment setup and both model downloads before class, but do not run seed_knowledge or index_knowledge in the participant database. Exercise 1 starts empty; students load documents, inspect the pre-index state and build their own index in Exercise 2. Run `python scripts/verify_workshop.py` in starter: it requires inherited controls and normal RAG operation while the RAG health check verifies the intended new weaknesses. Do not run the whole test suite as a readiness expectation for the untouched starter: new RAG security tests intentionally fail.

Run `python scripts/verify_workshop.py` in solution. It requires all checks. Use `--semantic` when Ollama is available and record that mode. Health checks use temporary users, grants, databases and indexes; they do not approve browser accounts or reset documents.

## Teaching details

- Embeddings are not the answer model. Selecting Demo answers does not change the embedding provider. Demo embeddings have a manual synonym table and must never be described as learned semantic understanding.
- Have students inspect search before generation; a model refusal can hide an unsafe retrieval design.
- All four repairs live in `knowledge/controls.py`. Prompt-authority wording and the enabled NeMo flow are separate visible edits.
- Exercise 4 fixes prefiltering. Forged-candidate tests still fail until Exercise 5 adds the independent postfilter.
- Exercise 5 revalidates MCP-returned text, not just vector metadata. A returned source ID is not enough.
- Approving the synthetic injection in Exercise 6 deliberately separates provenance from content safety. Quarantine it again afterward; never teach an attacker-controlled metadata flag as a trust decision.
- NeMo inspects the retrieval stage even though the framework reuses input rails internally for the JSON envelope. Its verdict does not grant access.
- Grounding is extractive here. It can reject invented text and citations, but cannot prove relevance or the truth of an approved source. Do not describe it as complete hallucination prevention.
- The malicious instruction sample, false-fact sample and benign quotation show distinct failure modes. Pattern matching can overblock educational descriptions and miss subtle poisoning.
- Evaluation reports deliberately expose a false positive and a false negative; passing the implementation tests does not imply a perfect confusion matrix.
- Persisted runtime events contain hashes/IDs and verdicts. Browser Debug still contains the current retrieved content and must be treated as private evidence.

## Troubleshooting

Ask for the exercise, exact input, selected answer/embedding providers, observed stage and full error. A timeout is not an authorization denial. Restore service availability before evaluating a defense. For a changed source or embedding model, reindex; for prompt or NeMo changes, restart Django.

The complete fixture checker uses actual local MCP, Chroma and NeMo, but explicit deterministic answer/embedding fixtures. The optional live checker uses Ollama. A local check does not prove the Codespaces environment or optional Gemini provider was exercised. Record the environment actually verified.

## Source-document realism

See [corpus teaching notes](CORPUS.md). Every PDF contains ordinary operational content and department metadata. Do not put lesson explanations, expected findings, ownership-enforcement instructions or attack labels into source records. Keep the data-fiction disclaimer in course documentation. The attack bulletin contains an actual instruction payload; the false assessment states its false claim as a normal finding; the awareness bulletin is a genuine staff-facing description used to measure overblocking.
