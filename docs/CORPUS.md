# Source corpus and teaching notes

The PDFs are sample support records for the existing support portal. Names, identifiers, balances and assessment results were authored for the course. They do not establish official university policy. Normal procedural links refer only to implemented portal routes: `/tickets/new/` and `/tickets/`. The documents do not advertise an identity, payment, printing or booking website. The attack bulletin deliberately claims that account access was restored even though no such operation occurred.

This explanation belongs in the course material. It is deliberately absent from the PDFs and their document metadata so retrieval operates on ordinary-looking records without hints about the expected exercise outcome. Access decisions come from the manifest and application checks, not from statements inside a PDF.

| Source | Document type | Teaching use |
|---|---|---|
| account-recovery.pdf | Two-page account-access support procedure | Account-access support instructions, paraphrase retrieval and page provenance |
| wireless-access.pdf | Wireless issue support procedure | Normal operational guidance and a separate retrieval topic |
| printing.pdf | Printing issue support guide | Issue descriptions and support-request search questions |
| study-support.pdf | Academic support request guide | Advising, registration and support-request questions |
| alice-billing.pdf | Alice Morgan's billing statement | Account-owner isolation using line items, dates and a balance |
| bob-billing.pdf | Bob Chen's billing statement | Cross-user retrieval test using a different statement and balance |
| it-bulletin-2026-17.pdf | Purported IT service bulletin | Indirect injection embedded in a processing note; no classroom canary |
| security-awareness-2026-11.pdf | Employee security-awareness bulletin | A legitimate quotation that a phrase-based guardrail can overblock |

The last three live in the `poisoned/` exercise directory; that directory name and the manifest's classification are not supplied as source text to the model. Source identifiers and titles are ordinary document identifiers, rather than labels such as "poison" or "unverified." The awareness bulletin is benign despite being packaged beside the attack cases.

## Refreshing a previously imported version

From the activated application's directory:

```powershell
python manage.py seed_knowledge --poison --refresh
python manage.py index_knowledge
```

The refresh updates extracted text, titles and source information for existing document identifiers, increments changed revisions, and preserves existing ownership and approval decisions. If you have not yet imported the corpus, follow Exercise 2 normally; do not run these commands as part of initial environment setup.

## Where imported documents are stored

PDF files stay in `knowledge/corpus/`. `seed_knowledge` saves their extracted text and metadata in SQLite’s `knowledge_document` table; it does not save the PDF binary. Exact tokens searches the page text already in `knowledge_document`. `index_knowledge` then creates and embeds chunks in `knowledge_passage` and writes vectors, passage IDs and reference metadata to Chroma. See [Exercise 2](EXERCISES.md#what-the-import-and-index-commands-store) for the storage table and command source paths.
