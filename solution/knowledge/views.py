import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from chatbot.ai_client import AIClientError
from guardrails.runtime import GuardrailBlocked
from security.mcp_authorization import authorization_status
from security.redaction import sanitize
from .embeddings import model_name
from .models import Document, RetrievalEvent
from .pipeline import answer

@never_cache
@login_required
def workspace(request):
    error, turn = None, None
    question = ''
    provider = request.POST.get('provider',request.session.get('rag_provider','qwen'))
    if provider not in {'qwen','mock','gemini'}:
        provider = 'qwen'
    if request.method=='POST':
        if request.POST.get('action')=='clear':
            request.session.pop('rag_last_turn',None)
            return redirect('knowledge_workspace')
        request.session['rag_provider'] = provider
        question = request.POST.get('question','')
        if len(question)>2000:
            return HttpResponseBadRequest('Question exceeds 2000 characters.')
        if not request.session.session_key:
            request.session.create()
        try:
            turn = answer(request.user,question,provider,request.session.session_key,
                method=request.POST.get('method','vector'),search_only=request.POST.get('action')=='search')
        except (GuardrailBlocked,PermissionError,RuntimeError,AIClientError,ValueError) as exc:
            error = sanitize(str(exc))
            turn = {'answer':None,'sources':[],'trace':getattr(exc,'rag_trace',[]),
                    'prompts':getattr(exc,'rag_prompts',[]),'request_id':getattr(exc,'rag_request_id',None)}
        request.session['rag_last_turn'] = sanitize({'question':question,'turn':turn,'error':error})
    else:
        saved = request.session.get('rag_last_turn',{})
        question,turn,error = saved.get('question',''),saved.get('turn'),saved.get('error')
    grant, auth_error = authorization_status(request.user)
    # The ordinary catalog always protects owners; the vulnerable retrieval path is the exercise.
    from django.db.models import Q
    documents = Document.objects.filter(Q(visibility='shared')|Q(owner=request.user)).order_by('slug')
    return render(request,'knowledge/workspace.html',{'question':question,'turn':turn,'error':error,
        'provider':provider,'method':request.POST.get('method','vector'),'embedding_model':model_name(),'embedding_provider':settings.RAG_EMBEDDING_PROVIDER,
        'documents':documents,'authorization':grant,'authorization_error':auth_error,
        'nemo_enabled':settings.NEMO_CHECKS,'nemo_mode':settings.NEMO_POLICY_MODE,
        'inspection':json.dumps((turn or {}).get('trace',[]),indent=2,ensure_ascii=False),
        'prompts':json.dumps((turn or {}).get('prompts',[]),indent=2,ensure_ascii=False),
        'events':RetrievalEvent.objects.filter(actor=request.user).order_by('-id')[:8]})
