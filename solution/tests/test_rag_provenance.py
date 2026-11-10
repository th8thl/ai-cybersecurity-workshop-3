from unittest.mock import patch
from knowledge.retrieval import search
from .rag_common import RAGTestCase

class ProvenanceTests(RAGTestCase):
    @patch('knowledge.retrieval.candidates')
    def test_changed_source_body_invalidates_old_embedding(self,candidates):
        doc,p=self.source()
        doc.body='Changed policy';doc.save()
        candidates.return_value=[self.candidate(p)]
        self.assertEqual(search(self.alice,'password')['passages'],[])

    @patch('knowledge.retrieval.candidates')
    def test_forged_checksum_revision_or_model_is_rejected(self,candidates):
        _,p=self.source()
        for metadata in ({'checksum':'forged'},{'revision':99},{'model':'different'}):
            with self.subTest(metadata=metadata):
                candidates.return_value=[self.candidate(p,**metadata)]
                self.assertEqual(search(self.alice,'password')['passages'],[])

    @patch('knowledge.retrieval.candidates')
    def test_revoked_approval_is_checked_without_reindexing(self,candidates):
        doc,p=self.source()
        doc.approved=False;doc.save()
        candidates.return_value=[self.candidate(p)]
        self.assertEqual(search(self.alice,'password')['passages'],[])
