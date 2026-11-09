from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from security.redaction import sanitize
from .models import Document
from .retrieval import search


@never_cache
@login_required
def workspace(request):
    query = request.POST.get('question', '').strip()
    method = request.POST.get('method', 'keyword')
    result, error = None, None
    if request.method == 'POST':
        try:
            result = search(request.user, query, method, catalog_only=True)
        except (PermissionError, RuntimeError, ValueError) as exc:
            error = sanitize(str(exc))
    documents = Document.objects.filter(Q(visibility='shared') | Q(owner=request.user)).order_by('slug')
    return render(request, 'knowledge/workspace.html', {
        'question': query, 'method': method, 'result': result,
        'error': error, 'documents': documents,
    })
