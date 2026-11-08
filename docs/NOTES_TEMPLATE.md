# Session 3 evidence

Environment: ____  Date: ____  Answer provider/model: ____  Embedding provider/model: ____  NeMo mode: ____

## Retrieval and embeddings

| Question | Search mode | PDF filename, page, source IDs and rank | Distance | Dimensions | Supported/relevant? |
|---|---|---|---|---|---|
| | | | | | |

## Attack and repair evidence

| Exercise | Exact input / corpus change | Before behavior | Relevant code/check | After behavior | Legitimate request still works? |
|---|---|---|---|---|---|
| | | | | | |

Record document approval/owner, whether text reached the prompt, model behavior, runtime stage/verdict, and request ID separately. Do not copy raw credentials/tokens or another person's data.

## Evaluation

Dataset/mode: ____ TP: ____ FP: ____ FN: ____ TN: ____ Errors: ____ Precision: ____ Recall: ____

What was measured? ____ What was not measured? ____ One false positive: ____ One false negative: ____

## Final explanation

1. How does RAG connect company knowledge to a model without retraining?
2. How do embeddings support semantic search? What does cosine distance fail to tell you?
3. Where are permissions enforced if someone calls MCP directly?
4. Why are retrieved documents, metadata and MCP results untrusted?
5. What can source hashes, citations and exact-excerpt checks prove? What can they not prove?
6. How would you reconstruct a suspicious answer without logging raw private content?
7. Why is this context/data poisoning rather than true model poisoning?

Submit source changes, selected logs/tests and your threat model. Exclude .env, databases, vector indexes, environments and raw tokens.
