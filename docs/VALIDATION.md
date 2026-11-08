# Implementation validation

Verified locally on Windows with Python 3.13 and the pinned application dependencies on November 4, 2026.

| Check | Result |
|---|---|
| Final full solution test suite | 159 tests passed |
| Starter readiness suite | 139 tests passed; intended RAG weaknesses reproduced by baseline health check |
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
