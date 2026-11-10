"""The four focused Session 3 repair points. Keep Session 2 controls intact."""
from django.db.models import Q
from guardrails.runtime import check
from .models import Document, digest
from .grounding import validate_answer
from .pdf_sources import source_unchanged

def visible_documents(actor):
    return Document.objects.filter(Q(visibility='shared')|Q(owner=actor),approved=True)

def accept_document(document):
    return source_unchanged(document) and (
        not document.source_pages
        or document.body == '\n\n'.join(page['text'] for page in document.source_pages)
    )

def accept_passage(actor, passage, metadata):
    doc = passage.document
    allowed = doc.approved and (doc.visibility=='shared' or doc.owner_id==actor.pk)
    return (allowed and source_unchanged(doc) and passage.checksum==digest(passage.text)
        and passage.document_checksum==digest(doc.body) and passage.revision==doc.revision
        and metadata.get('model')==passage.embedding_model
        and metadata.get('checksum')==passage.checksum and metadata.get('revision')==doc.revision)

def check_retrieved(passages, provider, trace):
    check('retrieval',passages,provider,trace)

def check_answer(answer, passages):
    return validate_answer(answer,passages)
