# Implementation validation

Verified locally on Windows with Python 3.13 and the pinned application dependencies on November 4, 2026.

| Check | Result |
|---|---|
| Final full solution test suite | 165 tests passed |
| Starter readiness suite | 144 tests passed; intended RAG weaknesses reproduced by baseline health check |
| Complete documented starter and solution verification | Passed, including inherited ticket controls, MCP, real NeMo, Chroma and scanner assertions |
| Live RAG health check | Passed with Ollama `embeddinggemma:300m` and `qwen3:0.6b-q4_K_M` |
| Inherited live ticket-agent / semantic NeMo check | Passed with Qwen |
| Focused final runtime, grounding and interface regressions | 15 tests passed |
| Django migration consistency | No missing migrations |
| Codespaces Bash scripts | Syntax checked |
| Knowledge workspace and offline slides | Visually reviewed; navigation, Debug and 17-slide read view checked |
| Markdown file links and Python syntax | Checked |
| Starter / solution teaching differences | README, knowledge/controls.py, prompts/rag_policy.txt, guardrails/runtime.yml only |
| Original Session 2 repository | Git working tree remains clean |

Scanner results are review evidence, not a claim of zero weaknesses. The verified scan had zero Semgrep findings and no HIGH Bandit findings; review the retained lower-severity diagnostics in local `results/application/current/`.

The labeled deterministic context evaluation produced TP=3, FP=1, FN=2, TN=2, with no service errors. It intentionally exposes educational-quotation overblocking and missed approved misinformation/subtle instructions. It does not measure vector ranking or live-model attack success.

Codespaces configuration and setup were preserved and extended from Session 2, but an actual GitHub Codespace and GitHub Actions run were not launched from this local environment. Optional Gemini was not exercised. Those environments have their own documented checks.

Local starter setup includes its own generated configuration, synthetic demo accounts and migrated database. Knowledge ingestion and indexing are now student activities in Exercise 2; the originally generated local knowledge state was backed up and removed from the active starter. These runtime files are ignored by Git. Recover its generated demo logins with `python manage.py seed_demo --show-passwords` from the activated starter environment.

## PDF source upgrade

The distributed corpus now contains seven clean and three poisoned/training PDFs in each application, with a metadata-only manifest. All eleven source pages were rendered and visually checked. PDF ingestion extracts actual text with pypdf, retains original page numbers and hashes source bytes. It remains a student step; setup does not import or index the corpus. Scanned/image-only and encrypted PDFs produce explicit errors; OCR is not implemented.

The PDF-based starter and solution verification commands passed, including scanner assertions and actual MCP/Chroma/NeMo checks. The live PDF retrieval/generation check also passed after constraining provider output to supported excerpts. The final focused PDF/grounding checks passed 13 tests.

## Source realism revision

All ten documents in each application were rewritten as ordinary institutional records, including department-authored PDF metadata. All eleven source pages were rendered and visually reviewed. No source text or PDF metadata contains classroom disclaimers, synthetic-data labels, answer-key explanations or the former WORKSHOP-OVERRIDE marker. Attack and benign-control identifiers were changed to neutral bulletin/review identifiers. The refresh command adopts legacy identifiers and preserves permissions/approval while updating text and titles. The active participant database was left unchanged.

November 8, 2026: Source realism revision verified with 164 solution tests, 143 starter readiness checks, complete process-level verification for both copies, and live Ollama/Qwen retrieval. Eighteen focused PDF/grounding checks passed. Evaluation metadata uses normal record titles and opaque source identifiers; expected labels remain outside model-visible context. PDF files are explicitly marked binary in Git attributes.

## Functional-reference correction

Removed the invented institutional identity and all external URL placeholders from every corpus PDF and its metadata. Normal procedural references now use only implemented `/tickets/new/` and `/tickets/` routes and the actual 120-character Request summary field. The corpus does not advertise identity reset, payment, print-release or appointment-booking portals. The malicious bulletin now attempts a false account-restoration claim instead of advertising a credential-collection URL. All eleven pages were rendered and visually checked; both billing statements fit one page.

Verification: 165 solution tests and 144 starter readiness tests passed. The final PDF/grounding regression group passed 19 tests. The starter RAG process check passed with the document-specific billing-statement query, and the solution RAG process check passed with live Ollama embeddings and Qwen against the final PDFs. The working participant database remained unchanged and empty.
