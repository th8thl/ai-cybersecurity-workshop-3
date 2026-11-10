"""Repair these four RAG boundaries; Session 2 ticket defenses are already complete."""
from django.db.models import Q
from guardrails.runtime import check
from .models import Document, digest
from .embeddings import model_name
from .grounding import validate_answer
from .pdf_sources import source_unchanged

def visible_documents(actor):
    # Exercise 4: uncomment the filter below and comment out the unfiltered return.
    # return Document.objects.filter(
    #     Q(visibility='shared') | Q(owner=actor),
    #     approved=True,
    # )
    return Document.objects.all()

def accept_document(document):
    # Exercise 5a: uncomment the whole check and comment out the final return.
    # # Compare the PDF on disk with the SHA-256 hash saved at import.
    # if not source_unchanged(document):
    #     return False

    # # If page text was saved, check that it reconstructs the full saved text.
    # if document.source_pages:
    #     page_text = '\n\n'.join(page['text'] for page in document.source_pages)
    #     return document.body == page_text
    # return True
    # Before Exercise 5a, accept every document.
    return True

def accept_passage(actor, passage, metadata):
    # Exercise 5b: uncomment the block below.
    # # Read current permissions and revision from the saved document.
    # doc = passage.document
    # allowed = doc.approved and (doc.visibility=='shared' or doc.owner_id==actor.pk)
    # # Compare the indexed passage and Chroma metadata with the saved records.
    # return (allowed and source_unchanged(doc) and passage.checksum==digest(passage.text)
    #     and passage.document_checksum==digest(doc.body) and passage.revision==doc.revision
    #     and metadata.get('model')==passage.embedding_model
    #     and metadata.get('checksum')==passage.checksum and metadata.get('revision')==doc.revision)
    # End Exercise 5b
    return True

def check_retrieved(passages, provider, trace):
    # Exercise 6: remove the # and space from the next line.
    # check('retrieval', passages, provider, trace)
    return None

def check_answer(answer, passages):
    # Exercise 7: remove the # and space from the next line.
    # return validate_answer(answer, passages)
    return answer
