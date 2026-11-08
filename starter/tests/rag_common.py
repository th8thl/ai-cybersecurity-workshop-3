from tempfile import TemporaryDirectory
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from knowledge.models import Document, Passage, digest
from knowledge.embeddings import demo_vector
from security.mcp_authorization import issue_grant, use_access_token, COOKIE_NAME

@override_settings(MCP_TRANSPORT='inprocess-test',NEMO_CHECKS=False,RAG_EMBEDDING_PROVIDER='demo',
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class RAGTestCase(TestCase):
    def setUp(self):
        self.alice=get_user_model().objects.create_user('alice')
        self.bob=get_user_model().objects.create_user('bob')
        _,self.token=issue_grant(self.alice,['knowledge:read'])
        self.enterContext(use_access_token(self.token))
        self.client.force_login(self.alice)
        self.client.cookies[COOKIE_NAME]=self.token
        self.directory=self.enterContext(TemporaryDirectory(prefix='rag-tests-',ignore_cleanup_errors=True))
        self.enterContext(override_settings(RAG_INDEX_DIR=self.directory))

    def source(self,slug='account',text='Use the official password recovery portal.',**fields):
        defaults={'title':slug,'body':text,'source':'workshop://'+slug,'visibility':'shared','approved':True}
        defaults.update(fields)
        doc=Document.objects.create(slug=slug,**defaults)
        p=Passage.objects.create(document=doc,ordinal=1,text=text,checksum=digest(text),
            document_checksum=digest(text),revision=1,embedding_model='demo-synonyms-v1',vector=demo_vector(text))
        return doc,p

    def candidate(self,p,**metadata):
        meta={'checksum':p.checksum,'revision':p.revision,'model':p.embedding_model}
        meta.update(metadata)
        return {'id':p.pk,'distance':0.1,'metadata':meta}

    def envelope(self,p):
        return {'id':p.document.slug+':1','document_id':p.document_id,'title':p.document.title,
                'text':p.text,'source':p.document.source,'revision':p.revision,'checksum':p.checksum,
                'distance':0.1,'approved':p.document.approved,'embedding_model':p.embedding_model}
