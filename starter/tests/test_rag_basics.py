from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from knowledge.ingestion import chunks,index_document
from knowledge.embeddings import embed,EmbeddingError
from knowledge.retrieval import search
from .rag_common import RAGTestCase

class ChunkTests(SimpleTestCase):
    def test_overlap_preserves_text_and_bounds(self):
        result=list(chunks('one two three four five six',words=4,overlap=1))
        self.assertEqual(result,['one two three four','four five six'])
        with self.assertRaises(ValueError):list(chunks('x',words=2,overlap=2))

    @override_settings(RAG_EMBEDDING_PROVIDER='ollama',RAG_EMBEDDING_MODEL='test')
    @patch('knowledge.embeddings.request.urlopen',side_effect=OSError('offline'))
    def test_embedding_failure_never_silently_switches_to_demo(self,_):
        with self.assertRaises(EmbeddingError):embed(['text'])

class RetrievalBasicsTests(RAGTestCase):
    @patch('knowledge.retrieval.candidates')
    def test_valid_semantic_result_exposes_vector_dimensions_and_source(self,candidates):
        _,p=self.source()
        candidates.return_value=[self.candidate(p)]
        result=search(self.alice,'I forgot my password')
        self.assertEqual(result['dimensions'],64)
        self.assertEqual(result['passages'][0]['id'],'account:1')
        self.assertEqual(result['passages'][0]['text'],p.text)

    def test_keyword_search_uses_exact_tokens(self):
        self.source(text='Account recovery portal')
        self.assertEqual(search(self.alice,'forgot credentials','keyword')['passages'],[])
        self.assertEqual(len(search(self.alice,'account recovery','keyword')['passages']),1)

    @patch('knowledge.ingestion.upsert')
    def test_index_records_content_hash_model_and_bounded_chunks(self,upsert):
        doc,_=self.source(text='Password recovery instructions.')
        self.assertEqual(index_document(doc),1)
        p=doc.passages.get()
        self.assertEqual(p.embedding_model,'demo-synonyms-v1')
        self.assertEqual(len(p.vector),64)
        upsert.assert_called_once()

    @patch('knowledge.retrieval.candidates',return_value=[])
    def test_empty_retrieval_is_not_a_service_error(self,_):
        self.assertEqual(search(self.alice,'unknown topic')['passages'],[])
