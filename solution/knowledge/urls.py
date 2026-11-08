from django.urls import path
from .views import workspace

urlpatterns = [path('',workspace,name='knowledge_workspace')]
