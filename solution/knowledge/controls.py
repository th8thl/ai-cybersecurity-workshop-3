"""The four focused Session 3 repair points. Keep Session 2 controls intact."""
from django.db.models import Q
from guardrails.runtime import check
from .models import Document, digest
from .embeddings import model_name
from .grounding import validate_answer
from .pdf_sources import source_unchanged

def visible_documents(actor):
    return Document.objects.filter(Q(visibility='shared')|Q(owner=actor),approved=True)

def accept_passage(actor, passage, metadata):
    doc = passage.document
    allowed = doc.approved and (doc.visibility=='shared' or doc.owner_id==actor.pk)
    return (allowed and source_unchanged(doc) and passage.checksum==digest(passage.text)
        and passage.document_checksum==digest(doc.body) and passage.revision==doc.revision
        and passage.embedding_model==model_name() and metadata.get('model')==model_name()
        and metadata.get('checksum')==passage.checksum and metadata.get('revision')==doc.revision)

def check_retrieved(actor, passages, provider, trace):
    # Revalidate the MCP envelope against authoritative records before prompt construction.
    from .models import Passage
    for item in passages:
        try:
            slug,ordinal = item['id'].rsplit(':',1)
            p = Passage.objects.select_related('document').get(document__slug=slug,ordinal=int(ordinal))
            if (item['text']!=p.text or item['source']!=p.document.source
                or item['title']!=p.document.title or item.get('page',1)!=p.page or not accept_passage(actor,p,{
                    'checksum':item['checksum'],'revision':item['revision'],'model':item['embedding_model']})):
                raise ValueError('Unverified tool context.')
        except (Passage.DoesNotExist,KeyError,TypeError,ValueError) as exc:
            raise PermissionError('MCP context failed provenance validation.') from exc
    check('retrieval',passages,provider,trace)

def check_answer(answer, passages):
    return validate_answer(answer,passages)
