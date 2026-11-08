"""One local Chroma operation per process: release engine locks on process exit."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import time


@contextmanager
def index_lock(directory, timeout=40):
    """Serialize embedded-index access across Django, MCP and ingestion."""
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / '.workshop.lock').open('a+b') as stream:
        stream.write(b'0')
        stream.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                stream.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError('Knowledge index is busy. Retry after indexing completes.')
                time.sleep(0.05)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def operate(payload):
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(path=payload['path'],settings=Settings(anonymized_telemetry=False))
    store = client.get_or_create_collection(payload['collection'],embedding_function=None,
        metadata={'hnsw:space':'cosine'})
    if payload['operation'] == 'upsert':
        store.upsert(**payload['records'])
        return {'ok':True}
    if payload['operation'] == 'count':
        return {'count':store.count()}
    if payload['operation'] != 'query':
        raise ValueError('Unsupported vector operation.')
    if not store.count():
        raise RuntimeError('Knowledge index is empty. Run python manage.py index_knowledge.')
    ids = payload['document_ids']
    result = store.query(query_embeddings=[payload['vector']],n_results=min(payload['limit'],store.count()),
        where={'document_id':{'$in':ids}} if ids is not None else None,include=['distances','metadatas'])
    return {'candidates':[{'id':int(identifier),'distance':float(distance),'metadata':metadata}
        for identifier,distance,metadata in zip(result['ids'][0],result['distances'][0],result['metadatas'][0])]}


if __name__ == '__main__':
    payload = json.load(sys.stdin)
    # Hold the OS lock until process exit closes the embedded engine handles.
    with index_lock(Path(payload['path'])):
        try:
            result = operate(payload)
        except Exception as exc:
            result = {'error':str(exc)}
        sys.stdout.buffer.write(json.dumps(result).encode('utf-8') + b'\n')
        sys.stdout.buffer.flush()
        os._exit(0)
