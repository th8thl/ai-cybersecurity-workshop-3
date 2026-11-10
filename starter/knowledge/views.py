from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

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

@login_required
@require_POST
def set_approval(request, slug):
    if not request.user.is_staff or not request.user.has_perm('knowledge.change_document'):
        raise PermissionDenied
    approval = request.POST.get('approved')
    if approval not in {'true', 'false'}:
        return HttpResponseBadRequest('Choose Approve or Mark unreviewed.')
    document = get_object_or_404(
        Document.objects.filter(Q(visibility='shared') | Q(owner=request.user)), slug=slug
    )
    document.approved = approval == 'true'
    document.save(update_fields=['approved'])
    return redirect('knowledge_workspace')
