# NeMo checks used by the assistant

The inherited worker checks messages, tool proposals, tool results and final responses. Session 3 adds a separate `retrieval` stage. Ticket permissions and document access remain enforced in the application regardless of content verdicts.

From this application's activated environment, run:

```bash
python guardrails/worker.py
```

Follow [Session 3 Exercise 6](../../docs/EXERCISES.md#6-add-a-runtime-retrieval-check-and-fix-prompt-authority) for normal and malicious JSON envelopes. The worker uses the real Colang runtime; it does not generate answers.

`policy.py` implements checks; `runtime.co` defines flows; `runtime.yml` enables flows. The starter retains both Session 2 flows but omits `protect retrieved context` until Exercise 6. The solution enables it. Restart Django after configuration changes.

```bash
python guardrails/compare.py --configured
python manage.py test tests.test_rag_runtime
```

The first command verifies inherited rules. The second verifies the new retrieval boundary. Optional semantic NeMo checks require local Qwen; these are distinct from the model generating the final answer. A missing worker is a service error, never evidence of a successful policy rejection.
