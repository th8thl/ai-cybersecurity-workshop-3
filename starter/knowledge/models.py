"""SQLite is authoritative; vector-store metadata never establishes permissions."""
import hashlib
import uuid
from django.conf import settings
from django.db import models

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

class Document(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    body = models.TextField()
    source_file = models.CharField(max_length=200, blank=True)
    source_checksum = models.CharField(max_length=64, blank=True)
    source_pages = models.JSONField(default=list)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=12, choices=[('shared','Shared'),('private','Private')])
    approved = models.BooleanField(default=False)
    source = models.CharField(max_length=200)
    revision = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

class Passage(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='passages')
    ordinal = models.PositiveIntegerField()
    page = models.PositiveIntegerField(default=1)
    text = models.TextField()
    checksum = models.CharField(max_length=64)
    document_checksum = models.CharField(max_length=64)
    revision = models.PositiveIntegerField()
    embedding_model = models.CharField(max_length=160)
    vector = models.JSONField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['document','ordinal'],name='unique_document_passage')]

class RetrievalEvent(models.Model):
    request_id = models.UUIDField(default=uuid.uuid4, unique=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_fingerprint = models.CharField(max_length=64)
    question_digest = models.CharField(max_length=64)
    provider = models.CharField(max_length=20)
    outcome = models.CharField(max_length=32, default='started')
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
