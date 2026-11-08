# GitHub Codespaces setup

Use this Session 3 folder as the repository root. `.devcontainer/`, `.github/`, `starter/` and `solution/` must be at that root, matching Session 2. Upload source files, not `.env`, `.venv`, databases, vector indexes or results.

1. Open the repository in GitHub Codespaces. The configuration uses the same Python 3.12 development image as Session 2.
2. Wait for `.devcontainer/setup.sh`. It creates **starter/.venv**, installs pinned requirements, preserves or generates `.env`, migrates Django, installs/starts Ollama, downloads Qwen and EmbeddingGemma, seeds Alice/Bob. It leaves the knowledge base empty; students ingest documents and build their own index in Exercise 2.
3. Save the setup-generated passwords shown in the setup output. Post-attach displays the saved demo logins again. The website does not print passwords.
4. Open a terminal named **Website**. From the repository root:

```bash
cd starter
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

5. Open private port **8000** from the Ports panel. Sign in and open Tickets first. Then authorize **Search my permitted knowledge base** for 30 minutes and open Knowledge.

Setup does not install a second solution environment. Run the answer key only when the instructor asks. Port 8001 is reserved for that comparison. EmbeddingGemma is an additional download of approximately 622 MB; complete it before class. The first embedding/model load can take longer than later requests. Ollama runs locally at 11434; do not expose it as a public Codespaces port.

## Every new terminal

Rename exercise terminals **Checks**, **MCP** or **NeMo** and activate the same starter environment in each:

```bash
cd starter
source .venv/bin/activate
```

Do not create another environment for MCP, NeMo, embeddings or scanners. All processes use this interpreter.

## Recover setup without resetting student work

From `starter`, with its environment active:

```bash
python scripts/configure.py
python manage.py migrate
python manage.py seed_demo --show-passwords
```

`configure.py` preserves existing settings and secrets. `seed_knowledge` preserves existing documents; it does not reset your poisoning experiment or approval changes. If accounts do not yet exist, run `seed_demo` without `--show-passwords` once.

Check Ollama with `ollama list`. Restart it using `bash ../.devcontainer/start-ollama.sh`. Download missing models with `ollama pull qwen3:0.6b-q4_K_M` and `ollama pull embeddinggemma:300m`. An Ollama error is a setup failure, not evidence that a security defense blocked a request.

## Optional answer key

Stop the starter website or use 8001. From the repository root:

```bash
cd solution
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/configure.py
python manage.py migrate
python manage.py seed_demo
python manage.py seed_knowledge
python manage.py index_knowledge
python manage.py runserver 0.0.0.0:8001
```

The answer key has its own settings, credentials, SQLite database and Chroma index. Do not copy raw tokens, local secrets or databases between the two applications.
