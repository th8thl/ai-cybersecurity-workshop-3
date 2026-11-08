from unittest.mock import patch
from django.test import Client
from knowledge.models import RetrievalEvent
from .rag_common import RAGTestCase

class KnowledgeInterfaceTests(RAGTestCase):
    def test_login_required_catalog_hides_other_owner(self):
        self.source('bob',text='BOB-PRIVATE-CONTENT',owner=self.bob,visibility='private')
        response=self.client.get('/chatbot/knowledge/')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'BOB-PRIVATE-CONTENT')
        self.assertEqual(Client().get('/chatbot/knowledge/').status_code,302)

    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.alice)
        self.assertEqual(client.post('/chatbot/knowledge/',{'question':'password'}).status_code,403)

    @patch('knowledge.pipeline.call',return_value={'passages':[]})
    def test_last_turn_does_not_cross_browser_sessions_or_accounts(self,_):
        self.client.post('/chatbot/knowledge/',{'question':'ALICE-QUESTION','provider':'mock'})
        other=Client();other.force_login(self.alice)
        self.assertNotContains(other.get('/chatbot/knowledge/'),'ALICE-QUESTION')
        self.client.force_login(self.bob)
        # Django flushes an authenticated session when switching user identities.
        self.assertNotContains(self.client.get('/chatbot/knowledge/'),'ALICE-QUESTION')

    @patch('knowledge.pipeline.call',return_value={'passages':[]})
    def test_html_is_escaped_and_clear_is_post_only(self,_):
        response=self.client.post('/chatbot/knowledge/',{'question':'<script>alert(1)</script>','provider':'mock'})
        self.assertNotContains(response,'<script>alert(1)</script>')
        self.assertContains(response,'&lt;script&gt;')
        self.client.post('/chatbot/knowledge/',{'action':'clear'})
        self.assertNotIn('rag_last_turn',self.client.session)

    @patch('knowledge.pipeline.call',side_effect=RuntimeError('service offline'))
    def test_error_page_retains_safe_boundary_trace(self,_):
        response=self.client.post('/chatbot/knowledge/',{'question':'password','provider':'mock'})
        self.assertContains(response,'service offline')
        self.assertContains(response,'disabled')
        self.assertEqual(RetrievalEvent.objects.get().outcome,'error')
