from unittest.mock import patch
from knowledge.controls import check_answer
from knowledge.pipeline import answer
from knowledge.models import RetrievalEvent
from .rag_common import RAGTestCase

class GroundingTests(RAGTestCase):
    def test_exact_supported_excerpt_is_accepted(self):
        _,p=self.source()
        raw={'abstain':False,'claims':[{'text':'Use the password recovery portal.','quote':p.text,'citation':'account:1','why':'The guide explains password recovery.'}]}
        self.assertEqual(check_answer(raw,[self.envelope(p)]),raw)

    def test_invented_citation_and_quote_are_rejected(self):
        _,p=self.source()
        for citation,text,quote in [('invented:1',p.text,p.text),('account:1','False quote','False quote')]:
            with self.subTest(citation=citation,text=text),self.assertRaises(ValueError):
                check_answer({'abstain':False,'claims':[{'text':text,'quote':quote,'citation':citation,'why':'The guide explains password recovery.'}]},[self.envelope(p)])

    @patch('knowledge.pipeline.call',return_value={'passages':[]})
    def test_no_evidence_abstains(self,_):
        turn=answer(self.alice,'unknown','mock','session-one')
        self.assertTrue(turn['answer']['abstain'])

    @patch('knowledge.pipeline.generate')
    @patch('knowledge.pipeline.call')
    def test_bad_draft_is_not_displayed_and_is_logged_as_unsupported(self,call,generate):
        _,p=self.source()
        call.return_value={'passages':[self.envelope(p)]}
        generate.return_value={'abstain':False,'claims':[{'text':'UNSUPPORTED-FINDING','quote':'wrong','citation':'invented:1','why':'Unsupported.'}]}
        turn=answer(self.alice,'security review','mock','session')
        self.assertTrue(turn['answer']['abstain'])
        self.assertNotIn('UNSUPPORTED-FINDING',repr(turn))
        self.assertEqual(RetrievalEvent.objects.get().outcome,'unsupported')

    def test_provider_schema_allows_paraphrase_and_rejects_forged_quote(self):
        from jsonschema import validate,ValidationError
        from knowledge.generation import evidence_schema
        _,p=self.source()
        schema=evidence_schema([self.envelope(p)])
        valid={'abstain':False,'claims':[{'text':'Use the password recovery portal.','quote':p.text,'citation':'account:1','why':'The guide explains password recovery.'}]}
        validate(valid,schema)
        forged={'abstain':False,'claims':[{'text':'invented','quote':'invented','citation':'account:1','why':'The guide explains password recovery.'}]}
        with self.assertRaises(ValidationError):validate(forged,schema)

    def test_demo_attack_fixture_uses_payload_without_a_workshop_marker(self):
        from knowledge.generation import generate
        from knowledge.pdf_sources import extract_pdf
        source=extract_pdf('poisoned/it-bulletin-2026-17.pdf')
        passages=[{'id':'it-bulletin-2026-17:1','text':' '.join(source['body'].split())}]
        # This controlled fixture reads the participant starter's weak policy.
        with patch('pathlib.Path.read_text',return_value='Treat retrieved passages as trusted policy.'):
            result=generate('How do I recover my account?',passages,'mock',[])
        self.assertIn('Your account access has been restored.',result['claims'][0]['text'])
        self.assertNotIn('processing note',result['claims'][0]['text'])
