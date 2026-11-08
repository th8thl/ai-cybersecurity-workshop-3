# Session 3 participant application

This application extends the Session 2 **solution**. Existing ticket defenses remain enabled. Follow [setup](../docs/SETUP.md), [exercises](../docs/EXERCISES.md) and [verification](../docs/VERIFICATION.md).

Repair the four RAG boundaries in knowledge/controls.py, the RAG policy prompt and the retrieval NeMo flow. New security tests intentionally fail until their exercise.

One Python environment runs the Django website, MCP, NeMo, embeddings, tests and scanners. Local configuration belongs in .env, based on .env.example. Do not distribute credentials, databases or the .rag-index directory.
