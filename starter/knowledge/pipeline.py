"""RAG retrieval is read-only. Retrieved instructions never authorize ticket actions."""
from time import perf_counter
from jsonschema import ValidationError
from django.conf import settings
from chatbot.mcp_client import call
from guardrails.runtime import check, GuardrailBlocked
from security.mcp_authorization import require_authorization
from security.redaction import sanitize
from . import controls
from .generation import generate
from .models import RetrievalEvent, digest

def answer(actor,question,provider,session_key,method='vector',search_only=False):
    require_authorization(actor,'knowledge:read')
    if not isinstance(question,str) or not 1<=len(question.strip())<=2000:
        raise ValueError('Enter a question between 1 and 2000 characters.')
    question = sanitize(question.strip())
    trace, prompts = [], []
    started = perf_counter()
    event = RetrievalEvent.objects.create(actor=actor,session_fingerprint=digest(session_key),
        question_digest=digest(question),provider=provider)
    outcome = 'error'
    result = None
    try:
        check('input',question,provider,trace)
        check('tool',{'tool':'search_knowledge','arguments':{'question':question,'method':method}},provider,trace)
        result = call(actor,'search_knowledge',{'question':question,'method':method})
        # Tool/MCP results are untrusted. Redact before Debug or model use.
        result = sanitize(result)
        check('tool_result',result,provider,trace)
        controls.check_retrieved(result['passages'],provider,trace)
        trace.append({'retrieval':result})
        if search_only:
            outcome = 'searched'
            return {'answer':None,'sources':result['passages'],'trace':trace,'prompts':prompts,'request_id':str(event.request_id)}
        raw = generate(question,result['passages'],provider,prompts)
        if provider == 'qwen':
            check('output', raw, provider, trace)
            outcome = 'answered' if raw else 'abstained'
            return {'answer': {'abstain': not raw, 'claims': [], 'text': sanitize(raw)},
                    'sources': result['passages'], 'trace': trace, 'prompts': prompts,
                    'request_id': str(event.request_id)}
        try:
            checked = controls.check_answer(raw,result['passages'])
        except (ValueError,ValidationError,TypeError,KeyError):
            outcome = 'unsupported'
            trace.append({'output_validation':'unsupported claim or malformed citation rejected'})
            return {'answer':{'abstain':True,'claims':[]},'sources':result['passages'],
                    'trace':trace,'prompts':prompts,'request_id':str(event.request_id),
                    'notice':'The draft answer failed source validation; no claims were displayed.'}
        check('output',checked,provider,trace)
        outcome = 'abstained' if checked['abstain'] else 'answered'
        trace.append({'output_validation':'completed','abstained':checked['abstain']})
        return {'answer':sanitize(checked),'sources':result['passages'],'trace':trace,
                'prompts':prompts,'request_id':str(event.request_id)}
    except Exception as exc:
        if isinstance(exc,GuardrailBlocked):
            verdict = next((row for row in reversed(trace) if 'allowed' in row),None)
            outcome = 'blocked' if verdict and verdict.get('allowed') is False and not verdict.get('error') else 'error'
        elif isinstance(exc,PermissionError):
            outcome = 'blocked'
        exc.rag_trace = sanitize(trace)
        exc.rag_prompts = sanitize(prompts)
        exc.rag_request_id = str(event.request_id)
        raise
    finally:
        event.outcome = outcome
        # No raw question, passage, model draft, token or secret in persistent telemetry.
        event.details = {'source_ids':[p['id'] for p in (result or {}).get('passages',[])],
            'elapsed_ms':round((perf_counter()-started)*1000),
            'embedding_model':(result or {}).get('embedding_model'),
            'method':method,'nemo_enabled':settings.NEMO_CHECKS,
            'checks':[{k:v for k,v in row.items() if k in {'stage','engine','mode','allowed','active_flows','skipped'}}
                      for row in trace if 'stage' in row]}
        event.save(update_fields=['outcome','details'])
