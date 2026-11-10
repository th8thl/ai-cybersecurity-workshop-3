from django.urls import path
from . import views, authorization_views

urlpatterns = [
    path("authorization/", authorization_views.authorize_assistant, name="assistant_authorization"),
    path("authorization/revoke/", authorization_views.revoke_assistant, name="assistant_revoke"),
    path("clear/", views.clear_history, name="assistant_clear_history"),
    path("", views.chat, name="assistant"),
]
