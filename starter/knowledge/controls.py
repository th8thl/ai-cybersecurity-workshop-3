"""Repair these four RAG boundaries; Session 2 ticket defenses are already complete."""
from django.db.models import Q
from guardrails.runtime import check
from .models import Document, digest
from .embeddings import model_name
from .grounding import validate_answer
from .pdf_sources import source_unchanged

def visible_documents(actor):
    # Exercise 4: limit retrieval to approved shared documents or this actor's own.
    return Document.objects.all()

def accept_document(document):
    # Exercise 5: verify the imported PDF and its extracted page text.
    return True

def accept_passage(actor, passage, metadata):
    # Exercise 5: recheck permission, approval, content hash, revision and embedding identity.
    return True

def check_retrieved(actor, passages, provider, trace):
    # Exercise 6: run the retrieval boundary through NeMo, then enable its flow.
    return None

def check_answer(answer, passages):
    # Exercise 7: reject invented citations, mismatched quotes and unsupported claims.
    return answer
