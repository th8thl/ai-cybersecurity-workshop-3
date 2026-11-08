# Local setup

Use Python **3.12 or 3.13**, matching Session 2. Install Ollama from its official distribution and ensure the local service is running. Use one environment for all workshop tools.

## Continue an existing local installation

If you already completed setup, keep your existing environment, `.env`, database and exercise changes. Do not recreate `.venv` or restart the workshop simply because the source files were updated.

For normal daily startup, from **inside `starter`**:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

If you have received source updates since your last setup, stop the running website with Ctrl+C and apply dependencies/migrations once, from the same folder:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/configure.py
python manage.py migrate
python manage.py runserver
```

These are update steps, not a data reset. Do not load or index knowledge during environment setup. Exercise 1 inspects the empty catalog; Exercise 2 runs `seed_knowledge` to extract the PDFs and `index_knowledge` to build embeddings and the vector index. If you have already completed Exercise 2, keep that populated state and continue to the next exercise rather than deleting it to recreate Exercise 1.

The initial setup commands below are for a **fresh checkout** that has no environment or demo accounts yet.

## First-time Windows setup — repository root

```powershell
cd starter
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/configure.py
python manage.py migrate
python manage.py seed_demo
ollama pull qwen3:0.6b-q4_K_M
ollama pull embeddinggemma:300m
python manage.py runserver
```

## First-time macOS/Linux setup — repository root

```bash
cd starter
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/configure.py
python manage.py migrate
python manage.py seed_demo
ollama pull qwen3:0.6b-q4_K_M
ollama pull embeddinggemma:300m
python manage.py runserver
```

Setup leaves the knowledge base empty. Students load documents and build the index in Exercise 2.

Open `http://127.0.0.1:8000/tickets/`. Save the generated demo passwords. Authorize knowledge access separately in the website. In each new terminal activate this same environment.

## Environment variables

All existing Session 2 variables retain their names and meaning: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, optional CSRF origins, `AI_PROVIDER`, `QWEN_MODEL`, `QWEN_API_URL`, optional Gemini settings, `NEMO_ENABLED`, and `NEMO_POLICY_MODE`. `.env.example` is distributable; `.env` is private. Secrets remain outside prompts and child-process configuration is explicitly allowlisted.

New settings:

| Variable | Default | Purpose |
|---|---|---|
| RAG_EMBEDDING_PROVIDER | ollama | Real learned embeddings; explicit `demo` is a fixed synonym fixture |
| RAG_EMBEDDING_MODEL | embeddinggemma:300m | Same embedding model for ingestion and questions |
| RAG_EMBEDDING_URL | http://127.0.0.1:11434/api/embed | Separate embedding endpoint |
| RAG_TOP_K | 3 | Maximum passages returned; 1–10 |
| RAG_MAX_DISTANCE | 0.75 | Cosine-distance cutoff; 0–2, calibrate with evidence |
| RAG_INDEX_DIR | application/.rag-index | Optional local index override |

`WORKSHOP_RUNTIME_DB` and `WORKSHOP_RUNTIME_INDEX` are private integration-test/child-process overrides. They isolate temporary checks and should not be set for ordinary class use. Changing an embedding model requires reindexing. Collections are separated by embedding identity.

For a model-free fallback, explicitly set `RAG_EMBEDDING_PROVIDER=demo` in `.env`, restart Django, run `index_knowledge`, and choose **Demo** in the Knowledge page. The UI and traces label this mode. Return to `ollama`, reindex and restart to demonstrate learned semantic retrieval. A fallback run is not evidence about Qwen or EmbeddingGemma.

The inherited `AI_PROVIDER` setting is retained; the ticket assistant and knowledge workspace default to Qwen and remember browser selections, matching the Session 2 interface behavior. Selecting Demo answers does not change the embedding provider.
