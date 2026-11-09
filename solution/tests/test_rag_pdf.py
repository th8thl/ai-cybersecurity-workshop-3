from pathlib import Path
from io import StringIO
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings
from pypdf import PdfWriter
from knowledge.pdf_sources import extract_pdf, source_unchanged, manifest
from knowledge.ingestion import index_document
from knowledge.models import Document, Passage
from .rag_common import RAGTestCase


class PDFExtractionTests(SimpleTestCase):
    def test_actual_pdf_extraction_preserves_page_numbers(self):
        result = extract_pdf('clean/account-recovery.pdf')
        self.assertEqual([p['page'] for p in result['source_pages']],[1,2])
        self.assertIn('/tickets/new/',result['source_pages'][0]['text'])
        self.assertIn('Before you begin',result['source_pages'][1]['text'])
        self.assertEqual(len(result['source_checksum']),64)

    def test_source_pdfs_and_metadata_do_not_reveal_exercise_answers(self):
        from pypdf import PdfReader
        forbidden=('synthetic','fictional','workshop','supplied evidence',
                   'assistant access','shared technical index','account boundary')
        for row in manifest():
            with self.subTest(document=row['file']):
                extracted=extract_pdf(row['file'])
                pdf=PdfReader(settings.BASE_DIR/'knowledge/corpus'/row['file'])
                content=(extracted['body']+' '+str(pdf.metadata)).casefold()
                self.assertFalse(any(term in content for term in forbidden),row['file'])
                self.assertNotIn('poison',row['slug'])
                self.assertNotIn('unverified',row['title'].casefold())

    def test_documents_do_not_advertise_invented_sites_or_services(self):
        from django.urls import resolve
        from pypdf import PdfReader
        for row in manifest():
            with self.subTest(document=row['file']):
                text=extract_pdf(row['file'])['body']
                metadata=str(PdfReader(settings.BASE_DIR/'knowledge/corpus'/row['file']).metadata)
                content=(text+' '+metadata).casefold()
                for unsupported in ('juniper','jcu-','https://','http://','.example','.invalid',
                                    'identity portal','print portal','booking portal',
                                    'student accounts portal','student services, room'):
                    self.assertNotIn(unsupported,content)
        for route in ('/tickets/new/','/tickets/'):
            self.assertIn(resolve(route).url_name,{'ticket_create','ticket_list'})

    def test_billing_pdfs_are_statements_with_record_data(self):
        alice=extract_pdf('clean/alice-billing.pdf')['body']
        bob=extract_pdf('clean/bob-billing.pdf')['body']
        self.assertIn('Alice Morgan',alice)
        self.assertIn('Bob Chen',bob)
        self.assertIn('$25.00',alice)
        self.assertIn('$900.00',bob)
        for statement in (alice,bob):
            self.assertIn('Payment due',statement)
            self.assertIn('Account activity',statement)

    def test_manifest_contains_metadata_not_document_text(self):
        rows=manifest()
        self.assertEqual(len(rows),10)
        self.assertTrue(all('body' not in row and row['file'].endswith('.pdf') for row in rows))

    def test_pdf_paths_cannot_escape_corpus(self):
        for path in ('../outside.pdf','clean.json','https://example.com/file.pdf'):
            with self.subTest(path=path),self.assertRaises(ValueError):extract_pdf(path)

    def test_image_only_and_encrypted_pdfs_are_explicit_errors(self):
        with TemporaryDirectory() as directory:
            corpus=Path(directory)/'knowledge/corpus';corpus.mkdir(parents=True)
            for encrypted in (False,True):
                writer=PdfWriter();writer.add_blank_page(width=612,height=792)
                if encrypted:writer.encrypt('test-only-password')
                path=corpus/'fixture.pdf'
                with path.open('wb') as stream:writer.write(stream)
                with override_settings(BASE_DIR=Path(directory)),self.assertRaises(ValueError):
                    extract_pdf('fixture.pdf')

    def test_source_hash_detects_changed_pdf(self):
        doc=SimpleNamespace(source_file='clean/account-recovery.pdf',source_checksum='incorrect')
        self.assertFalse(source_unchanged(doc))


class PDFImportTests(RAGTestCase):
    def test_import_extracts_pdf_text_without_building_an_index(self):
        call_command('seed_knowledge',verbosity=0)
        self.assertEqual(Document.objects.count(),7)
        self.assertEqual(Passage.objects.count(), 0)
        self.assertFalse(Path(self.directory,'chroma.sqlite3').exists())
        doc=Document.objects.get(slug='account-recovery')
        self.assertEqual(len(doc.source_pages),2)
        self.assertEqual(doc.source,'account-recovery.pdf')
        self.assertEqual(Document.objects.get(slug='bob-billing').owner,self.bob)
        from knowledge.retrieval import search
        with patch('knowledge.retrieval.embed', side_effect=AssertionError('Keyword search used embeddings')):
            result = search(self.alice, 'account access', method='keyword')
        self.assertTrue(result['passages'])


    @patch('knowledge.ingestion.upsert')
    def test_index_keeps_pdf_page_provenance(self,_):
        call_command('seed_knowledge',verbosity=0)
        doc=Document.objects.get(slug='account-recovery')
        index_document(doc)
        self.assertEqual(set(doc.passages.values_list('page',flat=True)),{1,2})
        self.assertTrue(all(p.text in doc.source_pages[p.page-1]['text'].replace('\n',' ') for p in doc.passages.all()))

    def test_refresh_preserves_security_decisions_and_requires_reindex(self):
        call_command('seed_knowledge',verbosity=0)
        doc=Document.objects.get(slug='account-recovery')
        doc.approved=False;doc.source_checksum='old-version';doc.save()
        call_command('seed_knowledge',refresh=True,verbosity=0)
        doc.refresh_from_db()
        self.assertFalse(doc.approved)
        self.assertEqual(doc.revision,2)
        self.assertEqual(Passage.objects.count(), 0)

    def test_supplied_injection_can_be_enabled_for_runtime_exercise(self):
        call_command('seed_knowledge',poison=True,approve_lab_injection=True,stdout=StringIO())
        self.assertTrue(Document.objects.get(slug='it-bulletin-2026-17').approved)
