"""Bounded paragraph/word chunks; no document text is executed or fetched as a URL."""
from django.db import transaction
from .embeddings import embed, model_name
from .models import Document, Passage, digest
from .vector_store import upsert
from .pdf_sources import source_unchanged

def chunks(body, words=100, overlap=20):
    if not 0 <= overlap < words:
        raise ValueError('Overlap must be smaller than the chunk size.')
    for paragraph in body.split('\n\n'):
        tokens = paragraph.split()
        for start in range(0,len(tokens),words-overlap):
            yield ' '.join(tokens[start:start+words])
            if start+words >= len(tokens):
                break

def text_passages(document):
    pages = document.source_pages or [{'page': 1, 'text': document.body}]
    document_checksum = digest(document.body)
    parts = ((page['page'], text) for page in pages for text in chunks(page['text']))
    return [
        Passage(document=document, ordinal=ordinal, page=page, text=text,
                checksum=digest(text), document_checksum=document_checksum,
                revision=document.revision, embedding_model='', vector=[])
        for ordinal, (page, text) in enumerate(parts, 1)
    ]


def index_document(document):
    source_hash, revision = digest(document.body), document.revision
    if not source_unchanged(document):
        raise ValueError('Source PDF changed. Run seed_knowledge --refresh before indexing.')
    pages = document.source_pages or [{'page':1,'text':document.body}]
    if document.source_pages and document.body!='\n\n'.join(p['text'] for p in pages):
        raise ValueError('Extracted PDF text was edited independently of its page map. Re-import the PDF.')
    passages = text_passages(document)
    vectors = embed([passage.text for passage in passages])
    embedding_model = model_name()
    for passage, vector in zip(passages, vectors):
        passage.embedding_model = embedding_model
        passage.vector = vector
    with transaction.atomic():
        document = Document.objects.select_for_update().get(pk=document.pk)
        if digest(document.body)!=source_hash or document.revision!=revision or not source_unchanged(document):
            raise ValueError('Document changed while embedding. Run index_knowledge again.')
        document.passages.all().delete()
        Passage.objects.bulk_create(passages)
    # Old vector IDs are harmless: retrieval rechecks their live SQLite rows.
    # If Chroma fails, rerun index_knowledge; no stale vector is trusted.
    upsert(passages)
    return len(passages)
