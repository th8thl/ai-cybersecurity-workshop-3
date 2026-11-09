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

def check_retrieved(actor, passages, provider, trace):
    # Revalidate the MCP envelope against authoritative records before prompt construction.
    from .models import Passage
    from .retrieval import document_page
    for item in passages:
        try:
            slug,ordinal = item['id'].rsplit(':',1)
            if ordinal.startswith('page-'):
                page = int(ordinal.removeprefix('page-'))
                doc = visible_documents(actor).get(slug=slug)
                text = document_page(doc, page)
                if (text is None or not accept_document(doc) or item['text'] != text
                    or item['source'] != doc.source or item['title'] != doc.title
                    or item['page'] != page or item['revision'] != doc.revision
                    or item['checksum'] != digest(text) or item['embedding_model'] != ''):
                    raise ValueError('Unverified document page.')
                continue
            p = Passage.objects.select_related('document').get(document__slug=slug,ordinal=int(ordinal))
            if (item['text']!=p.text or item['source']!=p.document.source
                or item['title']!=p.document.title or item.get('page',1)!=p.page or not accept_passage(actor,p,{
                    'checksum':item['checksum'],'revision':item['revision'],'model':item['embedding_model']})):
                raise ValueError('Unverified tool context.')
        except (Document.DoesNotExist,Passage.DoesNotExist,KeyError,TypeError,ValueError) as exc:
            raise PermissionError('MCP context failed provenance validation.') from exc
    check('retrieval',passages,provider,trace)

def check_answer(answer, passages):
    return validate_answer(answer,passages)
