from unittest.mock import patch
from knowledge.controls import check_answer
from knowledge.pipeline import answer
from knowledge.models import RetrievalEvent
from .rag_common import RAGTestCase

class GroundingTests(RAGTestCase):
    def test_exact_supported_excerpt_is_accepted(self):
        _,p=self.source()
        raw={'abstain':False,'claims':[{'text':p.text,'quote':p.text,'citation':'account:1'}]}
        self.assertEqual(check_answer(raw,[self.envelope(p)]),raw)

    def test_invented_citation_and_unsupported_claim_are_rejected(self):
        _,p=self.source()
        for citation,text,quote in [('invented:1',p.text,p.text),('account:1','An invented finding',p.text),('account:1','False quote','False quote')]:
            with self.subTest(citation=citation,text=text),self.assertRaises(ValueError):
                check_answer({'abstain':False,'claims':[{'text':text,'quote':quote,'citation':citation}]},[self.envelope(p)])

    @patch('knowledge.pipeline.call',return_value={'passages':[]})
    def test_no_evidence_abstains(self,_):
        turn=answer(self.alice,'unknown','mock','session-one')
        self.assertTrue(turn['answer']['abstain'])

    @patch('knowledge.pipeline.generate')
    @patch('knowledge.pipeline.call')
    def test_bad_draft_is_not_displayed_and_is_logged_as_unsupported(self,call,generate):
        _,p=self.source()
        call.return_value={'passages':[self.envelope(p)]}
        generate.return_value={'abstain':False,'claims':[{'text':'UNSUPPORTED-FINDING','quote':'wrong','citation':'invented:1'}]}
        turn=answer(self.alice,'security review','mock','session')
        self.assertTrue(turn['answer']['abstain'])
        self.assertNotIn('UNSUPPORTED-FINDING',repr(turn))
        self.assertEqual(RetrievalEvent.objects.get().outcome,'unsupported')

    def test_provider_schema_limits_choices_but_application_still_rejects_forged_text(self):
        from jsonschema import validate,ValidationError
        from knowledge.generation import evidence_schema
        _,p=self.source()
        schema=evidence_schema([self.envelope(p)])
        valid={'abstain':False,'claims':[{'text':p.text,'quote':p.text,'citation':'account:1'}]}
        validate(valid,schema)
        forged={'abstain':False,'claims':[{'text':'invented','quote':'invented','citation':'account:1'}]}
        with self.assertRaises(ValidationError):validate(forged,schema)
