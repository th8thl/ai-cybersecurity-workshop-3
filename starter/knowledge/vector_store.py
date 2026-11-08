"""Bounded vector worker; no persistent Chroma client in Django/MCP processes."""
import hashlib
import json
import os
import subprocess
import sys
from django.conf import settings
from .embeddings import model_name


def operation(kind, **fields):
    identity = hashlib.sha256(model_name().encode()).hexdigest()[:16]
    payload = {'operation':kind,'path':str(settings.RAG_INDEX_DIR),
               'collection':'knowledge-'+identity,**fields}
    env = {name:value for name,value in os.environ.items()
        if name.upper() in {'SYSTEMROOT','WINDIR','PATH','TEMP','TMP','HOME','USERPROFILE'}}
    env.update(PYTHONUTF8='1',ANONYMIZED_TELEMETRY='False')
    try:
        process = subprocess.run([sys.executable,str(settings.BASE_DIR/'knowledge/vector_worker.py')],
            input=json.dumps(payload),capture_output=True,text=True,encoding='utf-8',
            env=env,timeout=60,check=True)
        result = json.loads(process.stdout)
    except (subprocess.SubprocessError,ValueError,OSError) as exc:
        raise RuntimeError('Vector worker failed. Check dependencies and index availability; no retrieval succeeded.') from exc
    if 'error' in result:
        raise RuntimeError(result['error'])
    return result


def count():
    return operation('count')['count']


def upsert(passages):
    if passages:
        operation('upsert',records={'ids':[str(p.pk) for p in passages],
            'embeddings':[p.vector for p in passages],
            'metadatas':[{'document_id':p.document_id,'checksum':p.checksum,
                         'revision':p.revision,'model':p.embedding_model,'page':p.page} for p in passages]})


def candidates(vector, document_ids, limit):
    if document_ids == []:
        return []
    return operation('query',vector=vector,document_ids=document_ids,limit=limit)['candidates']
