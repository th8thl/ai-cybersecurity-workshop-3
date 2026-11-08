"""Structured, deliberately extractive answers make source support testable."""
import json
import re
from copy import deepcopy
from urllib import request
from django.conf import settings
from chatbot.ai_client import AIClientError
from security.redaction import sanitize

ANSWER_SCHEMA = {'type':'object','properties':{
    'abstain':{'type':'boolean'},'claims':{'type':'array','maxItems':3,'items':{
        'type':'object','properties':{'text':{'type':'string','minLength':1,'maxLength':1000},
        'citation':{'type':'string','maxLength':120},'quote':{'type':'string','minLength':1,'maxLength':1000}},
        'required':['text','citation','quote'],'additionalProperties':False}}},
    'required':['abstain','claims'],'additionalProperties':False}

def evidence_schema(passages):
    """Constrain provider output to selectable excerpts; still validate at runtime.

    A provider's format promise cannot replace application checks, and a source
    excerpt still may be irrelevant or factually wrong.
    """
    schema = deepcopy(ANSWER_SCHEMA)
    options = []
    for passage in passages:
        excerpts = re.split(r'(?<=[.!?])\s+',passage['text'])
        excerpts = [text for text in excerpts if 1 <= len(text) <= 1000][:8]
        for text in excerpts:
            options.append({'type':'object','properties':{
                'text':{'const':text},'quote':{'const':text},'citation':{'const':passage['id']}},
                'required':['text','quote','citation'],'additionalProperties':False})
    if options:
        schema['properties']['claims']['items']={'anyOf':options}
    else:
        schema['properties']['claims']['maxItems']=0
    return schema


def generate(question, passages, provider, debug):
    response_schema = evidence_schema(passages)
    policy = (settings.BASE_DIR/'prompts/rag_policy.txt').read_text(encoding='utf-8')
    policy += '\nReturn JSON matching this schema: '+json.dumps(response_schema)
    content = json.dumps({'question':question,'retrieved_passages':passages},ensure_ascii=False)
    debug.append(sanitize({'provider':provider,'system':policy,'user':content,'schema':response_schema}))
    if provider=='mock':
        # Deterministic vulnerable-response fixture. It is NOT evidence of Qwen behavior.
        if 'trusted policy' in policy.casefold():
            poison = next((p for p in passages if 'WORKSHOP-OVERRIDE:' in p['text']),None)
            if poison:
                claim = poison['text'].split('WORKSHOP-OVERRIDE:',1)[1].strip()
                return {'abstain':False,'claims':[{'text':claim,'quote':claim,'citation':poison['id']}]}
        if not passages:
            return {'abstain':True,'claims':[]}
        p = passages[0]
        quote = p['text'][:1000]
        return {'abstain':False,'claims':[{'text':quote,'quote':quote,'citation':p['id']}]}
    if provider=='qwen':
        payload = {'model':settings.QWEN_MODEL,'stream':False,'think':False,'format':response_schema,
            'options':{'temperature':0,'num_predict':700},
            'messages':[{'role':'system','content':policy},{'role':'user','content':content}]}
        req = request.Request(settings.QWEN_API_URL,data=json.dumps(payload).encode(),
                              headers={'Content-Type':'application/json'},method='POST')
        try:
            with request.urlopen(req,timeout=120) as response:
                return json.loads(json.loads(response.read())['message']['content'])
        except (OSError,ValueError,KeyError,TypeError) as exc:
            raise AIClientError('Qwen RAG generation failed. Check Ollama and QWEN_MODEL.') from exc
    if provider=='gemini':
        if not settings.GEMINI_API_KEY or not settings.GEMINI_MODEL:
            raise AIClientError('Set GEMINI_API_KEY and GEMINI_MODEL before selecting Gemini.')
        from google import genai
        try:
            response = genai.Client(api_key=settings.GEMINI_API_KEY).models.generate_content(
                model=settings.GEMINI_MODEL,contents=content,config={'system_instruction':policy,
                'response_mime_type':'application/json','response_json_schema':response_schema,'temperature':0})
            return json.loads(response.text)
        except Exception as exc:
            raise AIClientError('Gemini RAG generation failed.') from exc
    raise ValueError('Unknown provider.')
