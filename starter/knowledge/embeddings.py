"""Real semantic embeddings use Ollama; the explicit demo is a teaching fixture."""
import hashlib
import json
import math
import re
from urllib import request
from django.conf import settings

class EmbeddingError(RuntimeError):
    pass

def model_name():
    if settings.RAG_EMBEDDING_PROVIDER == 'demo':
        return 'demo-synonyms-v1'
    if settings.RAG_EMBEDDING_PROVIDER != 'ollama':
        raise EmbeddingError('RAG_EMBEDDING_PROVIDER must be ollama or demo.')
    return settings.RAG_EMBEDDING_MODEL

def demo_vector(text):
    # Manually chosen synonyms, NOT a learned embedding model or semantic benchmark.
    synonyms = {'forgot':'password','recover':'password','recovery':'password',
                'reset':'password','credentials':'password','signin':'password',
                'wireless':'wifi','network':'wifi','printing':'printer',
                'charges':'billing','fee':'billing','fees':'billing',
                'tutoring':'study','finals':'study'}
    vector = [0.0] * 64
    for token in re.findall(r'[a-z0-9]+',text.casefold()):
        if token in {'the','a','an','is','to','my','i','how','can','do','of','and','for','in'}:
            continue
        token = synonyms.get(token, token)
        slot = int(hashlib.sha256(token.encode()).hexdigest()[:8],16) % len(vector)
        vector[slot] += 1
    norm = math.sqrt(sum(x*x for x in vector)) or 1
    return [x/norm for x in vector]

def embed(texts):
    model_name()
    if not texts or any(not isinstance(t,str) or not t.strip() or len(t)>8000 for t in texts):
        raise EmbeddingError('Embedding inputs must be nonempty passages under 8000 characters.')
    if settings.RAG_EMBEDDING_PROVIDER == 'demo':
        return [demo_vector(t) for t in texts]
    payload = {'model':settings.RAG_EMBEDDING_MODEL,'input':texts,'truncate':False,
               'keep_alive':'0'}
    req = request.Request(settings.RAG_EMBEDDING_URL,data=json.dumps(payload).encode(),
                          headers={'Content-Type':'application/json'},method='POST')
    try:
        with request.urlopen(req,timeout=120) as response:
            vectors = json.loads(response.read())['embeddings']
        if len(vectors)!=len(texts) or not vectors or not vectors[0]:
            raise ValueError('Missing embeddings')
        dimensions = len(vectors[0])
        if any(len(v)!=dimensions or any(type(x) not in (float,int) or not math.isfinite(x) for x in v)
               or not any(v) for v in vectors):
            raise ValueError('Invalid embedding')
        return vectors
    except (OSError,KeyError,ValueError,TypeError) as exc:
        raise EmbeddingError('Embedding failed. Check Ollama, RAG_EMBEDDING_MODEL and /api/embed. No demo fallback was used.') from exc
