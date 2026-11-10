"""Labeled context-boundary evaluation; does not measure retrieval ranking or model replies."""
import argparse
import csv
from io import StringIO
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--semantic',action='store_true',help='Also use local Qwen as NeMo content classifier.')
args=parser.parse_args()
os.environ.setdefault('DJANGO_SETTINGS_MODULE','support_portal.settings')
os.environ.setdefault('DJANGO_SECRET_KEY','disposable-context-evaluation-key')

def main():
    rows=[]
    with TemporaryDirectory(prefix='rag-evaluation-') as directory:
        os.environ['WORKSHOP_RUNTIME_DB']=str(Path(directory)/'portal.sqlite3')
        import django
        django.setup()
        from django.conf import settings
        settings.RAG_EMBEDDING_PROVIDER='demo' # fixture vectors; this evaluation never searches an index
        settings.NEMO_CHECKS=True
        settings.NEMO_POLICY_MODE='semantic' if args.semantic else 'deterministic'
        from django.core.management import call_command
        from django.contrib.auth import get_user_model
        from django.db import connections
        from knowledge.models import Document,Passage,digest
        from knowledge.embeddings import demo_vector
        from knowledge.controls import check_retrieved
        from guardrails.runtime import close_worker,GuardrailBlocked
        try:
            call_command('migrate',verbosity=0,stdout=StringIO())
            alice=get_user_model().objects.create_user('alice')
            bob=get_user_model().objects.create_user('bob')
            with (root/'data/context_cases.csv').open(encoding='utf-8',newline='') as source:
                cases=list(csv.DictReader(source))
            for case in cases:
                owner={'alice':alice,'bob':bob}.get(case['owner'])
                reference='record-'+digest(case['id'])[:12]
                doc=Document.objects.create(slug=reference,title=case.get('title') or 'Service record',
                    body=case['text'],visibility=case['visibility'],owner=owner,
                    approved=case['approved']=='true',source=reference+'.pdf')
                p=Passage.objects.create(document=doc,ordinal=1,text=case['text'],
                    checksum=digest(case['text']),document_checksum=digest(case['text']),revision=1,
                    embedding_model='demo-synonyms-v1',vector=demo_vector(case['text']))
                payload={'id':doc.slug+':1','text':p.text,'source':doc.source,'title':doc.title,
                    'checksum':p.checksum,'revision':1,'embedding_model':p.embedding_model}
                trace=[]
                blocked=False;error=None
                try:
                    check_retrieved([payload],'qwen' if args.semantic else 'mock',trace)
                except GuardrailBlocked:
                    if not trace or trace[-1].get('error') or trace[-1].get('allowed') is not False:
                        error='Guardrail service failed; no content verdict.'
                    else:
                        blocked=True
                except Exception as exc:
                    error=type(exc).__name__
                rows.append({'id':case['id'],'category':case['category'],
                    'expected_blocked':case['expected_blocked']=='true','blocked':blocked,
                    'error':error,'stage':trace[-1].get('stage','provenance') if trace else 'provenance'})
        finally:
            close_worker();connections.close_all()
    valid=[r for r in rows if not r['error']]
    tp=sum(r['blocked'] and r['expected_blocked'] for r in valid)
    fp=sum(r['blocked'] and not r['expected_blocked'] for r in valid)
    fn=sum(not r['blocked'] and r['expected_blocked'] for r in valid)
    tn=sum(not r['blocked'] and not r['expected_blocked'] for r in valid)
    summary={'scope':'labeled context acceptance boundary; no vector ranking or answer-generation measurement',
        'positive_class':'unsafe context','mode':'semantic NeMo' if args.semantic else 'deterministic NeMo',
        'tp':tp,'fp':fp,'fn':fn,'tn':tn,'errors':len(rows)-len(valid),
        'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None,
        'limitations':'Approved misinformation and subtle instructions can pass; educational quotes can be overblocked.',
        'cases':rows}
    out=root/'results/rag-evaluation';out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    with (out/'cases.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,indent=2))
    if summary['errors']:raise SystemExit('Evaluation had service errors; inspect results before interpreting metrics.')

if __name__=='__main__':main()
