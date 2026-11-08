# Worked RAG findings

| Finding | Evidence | Classification | Repair |
|---|---|---|---|
| Cross-owner retrieval | Alice's search returns Bob's synthetic private billing passage | CWE-862 missing authorization | Pre/post retrieval ownership checks |
| Unreviewed/stale context trusted | Source text or approval changes after indexing; old candidate still accepted | CWE-345 insufficient verification of data authenticity | Authoritative approval/hash/revision/model checks |
| Retrieved instructions treated as policy | Document payload appears as trusted context and redirects fixture/model | CWE-20 input validation analogy; LLM prompt injection | Untrusted-evidence prompt plus runtime checks |
| Unsupported claim displayed | Invented source ID or quote passes to UI | CWE-20 output-validation weakness | Schema/citation/exact-excerpt validation |

CWE mappings describe aspects of the implementation, not a guarantee that every LLM issue fits one conventional category. Evaluate severity from actual data, reachability and impact. A fabricated CWE-89 claim in a document is itself evidence of poisoning, not proof that the application has SQL injection.
