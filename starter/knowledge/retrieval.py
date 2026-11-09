"""Shared website/MCP retrieval service, including authoritative authorization."""
import re
from django.conf import settings
from . import controls
from .embeddings import embed, model_name
from .models import Passage, digest
from .vector_store import candidates

def document_page(document, page):
    """Read one original PDF page from the imported document."""
    if not document.source_pages:
        return document.body if page == 1 else None
    return next((item['text'] for item in document.source_pages if item['page'] == page), None)


def keyword_search(documents, question):
    ignored = {'the', 'a', 'is', 'to', 'my', 'i', 'how', 'can', 'do'}
    terms = set(re.findall(r'[a-z0-9]+', question.casefold())) - ignored
    matches = []
    for doc in documents:
        if not controls.accept_document(doc):
            continue
        pages = doc.source_pages or [{'page': 1, 'text': doc.body}]
        for page in pages:
            text = page['text']
            matched_tokens = sorted(terms & set(re.findall(r'[a-z0-9]+', text.casefold())))
            if matched_tokens:
                number = page['page']
                matches.append({
                    'id': f'{doc.slug}:page-{number}', 'document_id': doc.pk,
                    'title': doc.title, 'text': text, 'source': doc.source,
                    'page': number, 'revision': doc.revision, 'checksum': digest(text),
                    'distance': round(1 - len(matched_tokens) / len(terms), 5),
                    'matched_tokens': matched_tokens,
                    'approved': doc.approved, 'embedding_model': '',
                })
    matches.sort(key=lambda item: (item['distance'], item['document_id'], item['page']))
    return {'passages': matches[:settings.RAG_TOP_K], 'method': 'keyword',
            'embedding_model': None, 'dimensions': None, 'vector_preview': [],
            'distance_note': 'Lower distance means more query tokens matched.'}


def search(actor, question, method='vector', *, catalog_only=False):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionError('Sign in before searching.')
    if not isinstance(question,str) or not 1 <= len(question.strip()) <= 2000:
        raise ValueError('Enter a question between 1 and 2000 characters.')
    if method not in {'vector','keyword'}:
        raise ValueError('Choose vector or keyword search.')
    documents = controls.visible_documents(actor)
    if catalog_only:
        from django.db.models import Q
        documents = documents.filter(Q(visibility="shared") | Q(owner=actor), approved=True)
    if method == 'keyword':
        return keyword_search(documents, question)
    ids = list(documents.values_list('pk', flat=True))
    vector = embed([question])[0]
    ranked = candidates(vector, ids, settings.RAG_TOP_K * 4)
    passages = []
    for candidate in ranked:
        p = Passage.objects.select_related('document').filter(pk=candidate['id']).first()
        if p is None or (catalog_only and p.document_id not in ids) or not controls.accept_passage(actor,p,candidate['metadata']):
            continue
        if p.embedding_model != model_name() or candidate['distance'] > settings.RAG_MAX_DISTANCE:
            continue
        passages.append({'id':f'{p.document.slug}:{p.ordinal}','document_id':p.document_id,
            'title':p.document.title,'text':p.text,'source':p.document.source,'page':p.page,
            'revision':p.revision,'checksum':p.checksum,'distance':round(candidate['distance'],5),
            'approved':p.document.approved,'embedding_model':p.embedding_model})
        if len(passages)>=settings.RAG_TOP_K:
            break
    return {'passages': passages, 'method': 'vector', 'embedding_model': model_name(),
            'dimensions': len(vector), 'vector_preview': vector[:8],
            'distance_note': 'Lower cosine distance means greater similarity.'}
