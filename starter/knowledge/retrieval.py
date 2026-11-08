"""Shared website/MCP retrieval service, including authoritative authorization."""
import re
from django.conf import settings
from . import controls
from .embeddings import embed, model_name
from .models import Passage
from .vector_store import candidates

def search(actor, question, method='vector'):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionError('Sign in before searching.')
    if not isinstance(question,str) or not 1 <= len(question.strip()) <= 2000:
        raise ValueError('Enter a question between 1 and 2000 characters.')
    if method not in {'vector','keyword'}:
        raise ValueError('Choose vector or keyword search.')
    documents = controls.visible_documents(actor)
    ids = list(documents.values_list('pk',flat=True))
    vector = embed([question])[0] if method=='vector' else None
    if method=='vector':
        ranked = candidates(vector,ids,settings.RAG_TOP_K*4)
    else:
        terms = set(re.findall(r'[a-z0-9]+',question.casefold())) - {'the','a','is','to','my','i','how','can','do'}
        scored = []
        for p in Passage.objects.filter(document_id__in=ids,embedding_model=model_name()):
            hits = len(terms & set(re.findall(r'[a-z0-9]+',p.text.casefold())))
            if hits:
                scored.append({'id':p.pk,'distance':1-hits/max(len(terms),1),'metadata':{'checksum':p.checksum,'revision':p.revision,'model':p.embedding_model}})
        ranked = sorted(scored,key=lambda row:(row['distance'],row['id']))[:settings.RAG_TOP_K*4]
    passages = []
    for candidate in ranked:
        p = Passage.objects.select_related('document').filter(pk=candidate['id']).first()
        if p is None or not controls.accept_passage(actor,p,candidate['metadata']):
            continue
        if method=='vector' and candidate['distance'] > settings.RAG_MAX_DISTANCE:
            continue
        passages.append({'id':f'{p.document.slug}:{p.ordinal}','document_id':p.document_id,
            'title':p.document.title,'text':p.text,'source':p.document.source,'page':p.page,
            'revision':p.revision,'checksum':p.checksum,'distance':round(candidate['distance'],5),
            'approved':p.document.approved,'embedding_model':p.embedding_model})
        if len(passages)>=settings.RAG_TOP_K:
            break
    return {'passages':passages,'method':method,'embedding_model':model_name(),
            'dimensions':len(vector) if vector is not None else None,
            'vector_preview':vector[:8] if vector is not None else [],
            'distance_note':'Lower cosine distance means greater similarity; it is not a trust or confidence score.'}
