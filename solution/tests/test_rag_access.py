from unittest.mock import patch
from knowledge.controls import visible_documents
from knowledge.retrieval import search
from security.mcp_authorization import issue_grant, use_access_token, MCPAuthorizationError
from chatbot.mcp_client import call
from .rag_common import RAGTestCase

class RetrievalAccessTests(RAGTestCase):
    def test_filter_excludes_other_owners_and_unapproved_sources(self):
        shared,_=self.source()
        own,_=self.source('alice',owner=self.alice,visibility='private')
        self.source('bob',owner=self.bob,visibility='private')
        self.source('unreviewed',approved=False)
        self.assertEqual(set(visible_documents(self.alice).values_list('pk',flat=True)),{shared.pk,own.pk})

    @patch('knowledge.retrieval.candidates')
    def test_vector_store_cannot_override_document_ownership(self,candidates):
        _,p=self.source('bob',owner=self.bob,visibility='private')
        candidates.return_value=[self.candidate(p)]
        self.assertEqual(search(self.alice,'password')['passages'],[])

    def test_keyword_path_enforces_the_same_permissions(self):
        self.source('bob',owner=self.bob,visibility='private')
        self.assertEqual(search(self.alice,'password','keyword')['passages'],[])

    def test_mcp_requires_dedicated_knowledge_scope_even_with_ticket_read(self):
        _,token=issue_grant(self.alice,['tickets:read'])
        with use_access_token(token),self.assertRaises(MCPAuthorizationError):
            call(self.alice,'search_knowledge',{'question':'password'})
