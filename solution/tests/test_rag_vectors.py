from knowledge.ingestion import index_document
from knowledge.retrieval import search
from knowledge.vector_store import count
from .rag_common import RAGTestCase

class RealChromaTests(RAGTestCase):
    def test_persistent_vector_search_and_keyword_comparison(self):
        doc,_=self.source(text='Account recovery: use the official password portal.')
        index_document(doc)
        self.assertEqual(search(self.alice,'forgot credentials')['passages'][0]['id'],'account:1')
        self.assertEqual(search(self.alice,'forgot credentials','keyword')['passages'],[])
        self.assertGreater(count(),0)
