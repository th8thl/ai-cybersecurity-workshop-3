from unittest.mock import patch
from django.test import Client
from .rag_common import RAGTestCase

class KnowledgeInterfaceTests(RAGTestCase):
    def test_login_required_catalog_hides_other_owner(self):
        self.source('bob',text='BOB-PRIVATE-CONTENT',owner=self.bob,visibility='private')
        response=self.client.get('/knowledge/')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'BOB-PRIVATE-CONTENT')
        self.assertEqual(Client().get('/knowledge/').status_code,302)

    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.alice)
        self.assertEqual(client.post('/knowledge/',{'question':'password'}).status_code,403)

    @patch('knowledge.pipeline.generate', side_effect=AssertionError('Search page invoked answer generation'))
    def test_exact_tokens_returns_sources_without_an_answer(self, _):
        self.source(text='Use the password reset page.')
        response = self.client.post('/knowledge/', {'question': 'password', 'method': 'keyword'})
        self.assertContains(response, 'Use the password reset page.')
        self.assertNotContains(response, 'Answer model')

    def test_query_is_escaped(self):
        response = self.client.post('/knowledge/', {'question': '<script>alert(1)</script>'})
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')

    @patch('knowledge.views.search', side_effect=RuntimeError('service offline'))
    def test_search_error_is_visible(self, _):
        response = self.client.post('/knowledge/', {'question': 'password', 'method': 'vector'})
        self.assertContains(response, 'service offline')

    @patch('knowledge.retrieval.candidates')
    def test_chatbot_answers_from_retrieved_evidence(self, candidates):
        _, passage = self.source(text='Reset your password from the account settings.')
        candidates.return_value = [self.candidate(passage)]
        response = self.client.post('/chatbot/', {
            'message': 'How do I reset my password?', 'provider': 'mock',
        })
        self.assertContains(response, 'Reset your password from the account settings.')
        self.assertContains(response, '<summary>Sources</summary>', html=True)
        self.assertContains(response, 'workshop://account')
        self.assertContains(response, 'Why this supports the answer:')
        other = Client()
        other.force_login(self.alice)
        self.assertNotContains(other.get('/chatbot/'), 'Reset your password from the account settings.')


    @patch('chatbot.views.plan', return_value={"tool": "get_ticket", "arguments": {"ticket_id": 1}})
    @patch('knowledge.pipeline.generate')
    @patch('knowledge.retrieval.candidates')
    def test_recovery_question_bypasses_ticket_planner(self, candidates, generate, plan):
        _, passage = self.source(text='Open New ticket to request help recovering access.')
        candidates.return_value = [self.candidate(passage)]
        generate.return_value = 'Start by opening a support request.'
        response = self.client.post('/chatbot/', {
            'message': 'How do I recover my account?', 'provider': 'qwen',
        })
        plan.assert_not_called()
        generate.assert_called_once()
        self.assertContains(response, 'Start by opening a support request.')
        self.assertContains(response, '<summary>Sources</summary>', html=True)
        self.assertNotContains(response, 'Ticket result')
