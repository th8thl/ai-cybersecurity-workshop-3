# RAG framework and techniques

Retrieval-Augmented Generation is an application architecture: retrieve relevant evidence, put it into a bounded model context, and generate an answer. It is not itself a model or a particular Python library. This project implements those stages directly in the existing Django/MCP architecture. Chroma supplies vector storage; Ollama supplies embeddings; Qwen or Gemini supplies answer generation. An orchestration package such as LangChain or LlamaIndex is optional and is not needed to teach these stages.

## Ingestion

`seed_knowledge` uses pypdf to extract the actual source PDFs into Django's SQLite database. The metadata-only manifest assigns file paths, ownership, visibility and approval; PDF metadata cannot grant trust. Extraction records each page, the relative PDF path and a SHA-256 hash of the file bytes. Scanned/image-only and encrypted PDFs are explicit errors; OCR is outside this lab. Trusted setup code assigns ownership, visibility and approval; a source title saying "approved" grants no authority. `index_knowledge` splits paragraphs into chunks of up to 100 words with 20-word overlap within each PDF page, calls the separate embedding model, and writes vectors and reference metadata to Chroma. SQLite retains source text, passage hashes, document hashes, revision and embedding identity. Inspect these in the Django shell.

## Embeddings and meaning

An embedding is a numerical representation learned by a model from patterns in text. Related text often lands near other related text. It approximates semantic similarity; it does not understand truth or grant trust. Numeric dimensions do not correspond neatly to individual human concepts.

The question and passages must use the same embedding model and compatible dimensions. Switching models selects a separate collection; reindex documents after a model change. No fallback silently substitutes Demo. Ingestion sets `truncate=False` so a context-window overflow is an error rather than hidden text loss.

`inspect_embedding` shows actual dimensions, a short numeric preview, and cosine similarity. Compare a paraphrase and an unrelated sentence. The comparison is an observation, not a universal guarantee about ranking.

## Retrieval

Semantic search embeds a question and asks Chroma for nearby vectors. The index uses cosine distance: smaller means more similar. The configured distance threshold can exclude weak matches but requires calibration; it is not an answer-confidence probability. The keyword comparison matches exact tokens and uses a different score; do not compare its numbers directly with cosine distance.

The solution applies approved/shared/owner restrictions before vector search, and rechecks every returned candidate against the current database afterward. Indexed metadata cannot authorize a user. Changed documents, revoked approval, mismatched hashes and old embeddings cannot become prompt content merely because Chroma ranked them highly. Keyword search uses the same permissions.

## Generation and grounding

The pipeline calls the authorized `search_knowledge` MCP tool, revalidates its returned sources, applies NeMo to retrieved content, and sends passages as untrusted evidence. Qwen returns plain text and the app displays the passages supplied to it. Gemini and Demo use structured claims for the citation validation exercise. Application code checks citation membership and verifies that each quote appears in its cited passage. Drafts that fail those checks become a visible abstention. No ticket write tools exist in this RAG pipeline.

The Assistant presents a paraphrased answer with a collapsible **Sources** section. For Qwen, each entry shows a retrieved passage with its filename and page. Evaluate relevance and factual support by comparing the claim with the source.

## Poisoning terminology

- Direct prompt injection: attacker instructions in the user's message.
- Indirect prompt injection: attacker instructions inside retrieved documents, metadata or tool results.
- Context/data poisoning: adding misleading or malicious knowledge so retrieval changes answers. It may contain false facts without any instruction override.
- True model poisoning: modifying training data, fine-tuning or weights. That is not performed in this lab.

## Why companies use it

Companies use retrieval to connect models with current, private organizational knowledge while retaining the ability to update sources independently of model training. Useful answers depend on finding relevant evidence and controlling which data reaches the model. This creates work in ingestion, search quality, permissions, provenance, evaluation and runtime monitoring.

Technical references: [Ollama embeddings API](https://docs.ollama.com/api/embed), [EmbeddingGemma](https://ollama.com/library/embeddinggemma), [Chroma metadata filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering).

Vector index operations run in a bounded local worker with a cross-process lock. Each worker exits after one Chroma operation, releasing embedded-engine handles before ingestion, Django or MCP opens the same index again. This requires no additional service or port.

Source edits: run `seed_knowledge --refresh` to re-extract changed PDF bytes, then `index_knowledge`. File-hash mismatches invalidate old sources in the solution. The importer preserves existing ownership and approval when refreshing; it does not build vectors. Retrieved sources show the filename and original page number.

For Gemini generation, the response schema supplies a bounded set of verbatim evidence excerpts. This improves consistency with small models. Application validation remains independent: an external provider or forged tool/model response can violate a requested format. Cited source support still does not establish relevance or truth.
