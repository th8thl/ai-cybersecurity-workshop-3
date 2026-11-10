# Session 3 matrix coverage and executable evidence

Mapped to **4 Session Matrix!D2:D13** and **Notes!A11:A13** in the supplied curriculum workbook.

| Planned topic | Student work | Implementation/evidence |
|---|---|---|
| RAG architecture and grounding | Trace ingestion → retrieval → generation | knowledge app, RAG_FRAMEWORK.md; Exercises 1–2 |
| Embeddings, vectors and semantic search | Inspect dimensions/similarity; compare paraphrases and keywords | embeddings.py, inspect_embedding, real Chroma; Exercise 2 |
| Retrieval quality | Compare rankings, chunk/overlap experiment, weak-match threshold | ingestion.py, retrieval.py, UI Debug |
| Knowledge base and synthetic documents | Seed and index clean/private/poisoned PDFs | corpus/, seed_knowledge, index_knowledge |
| Indirect injection and context/data poisoning | Add malicious instructions and false factual finding | poisoned/ PDFs; Exercises 3 and 6 |
| Metadata and provenance | Inspect IDs, hashes, revision, embedding identity and approval | controls.py; test_rag_provenance |
| MCP/RAG access boundaries | Scoped search; bypass website; reject forged actor | search_knowledge; exercise_rag_mcp; rag_healthcheck |
| Tool outputs as untrusted runtime context | Screen retrieved content before prompting | NeMo retrieval guard |
| User/session isolation | Alice/Bob private notes and separate browser last turns | test_rag_access/interface |
| Hallucinated citations | Check invented passage IDs and quotes against retrieved passages | Exercise 7 grounding tests |
| Runtime guardrail checks and bypasses | Real NeMo retrieval flow; approved injection; benign quote | policy.py/runtime.co/runtime.yml; test_rag_runtime |
| Runtime logs and monitoring | Correlate request/source IDs, verdicts and outcomes | RetrievalEvent, Debug |
| False positive/negative measurement | Labeled boundary evaluation with errors separated | data/context_cases.csv; evaluate_rag.py |
| Context vs true model poisoning | Explain that only retrieved documents change | RAG_FRAMEWORK.md; final evidence question |
| Threat model and reporting | Update boundaries and evidence table | THREAT_MODEL.md, NOTES_TEMPLATE.md |
| Real-world case discussion | Read primary EchoLeak disclosure, map untrusted context boundary | CASE_STUDY.md; instructor debrief |

The matrix lists Chroma plus FAISS or a vector database; this lab uses **Chroma**, not multiple vector engines. No model training, fine-tuning, complete semantic fact checker, production OAuth provider, remote MCP deployment or OS sandbox is claimed. RAG is taught as an architectural framework; an additional orchestration framework is not required.
