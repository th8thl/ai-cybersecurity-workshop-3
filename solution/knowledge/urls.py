from django.urls import path
from .views import set_approval, workspace

urlpatterns = [
    path('', workspace, name='knowledge_workspace'),
    path('<slug:slug>/approval/', set_approval, name='knowledge_set_approval'),
]
