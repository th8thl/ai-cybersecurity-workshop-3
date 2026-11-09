"""Extract bounded local PDFs; permissions come from the trusted manifest, not PDF metadata."""
import hashlib
import json
from pathlib import Path
from django.conf import settings
from pypdf import PdfReader


def corpus_path(relative):
    root = (settings.BASE_DIR / 'knowledge/corpus').resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path.suffix.lower() != '.pdf' or not path.is_file():
        raise ValueError('Choose an existing PDF inside knowledge/corpus.')
    return path


def file_digest(path):
    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError('Workshop PDFs must be no larger than 5 MB.')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_pdf(relative):
    path = corpus_path(relative)
    checksum = file_digest(path)
    reader = PdfReader(path)
    if reader.is_encrypted:
        raise ValueError('Encrypted PDFs are not supported in this lab.')
    if not 1 <= len(reader.pages) <= 50:
        raise ValueError('Workshop PDFs must contain 1 to 50 pages.')
    pages = []
    for number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        # Keep source content as written; page numbers are recorded separately.
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        lines = [line for line in lines if line != f'Page {number}']
        text = '\n'.join(lines).strip()
        if not text:
            raise ValueError(f'Page {number} has no extractable text; scanned/image PDFs require OCR, which this lab does not provide.')
        if len(text) > 50000:
            raise ValueError('PDF page text exceeds the workshop limit.')
        pages.append({'page':number,'text':text})
    if file_digest(path) != checksum:
        raise ValueError('PDF changed during extraction; import it again.')
    return {'body':'\n\n'.join(p['text'] for p in pages),'source_pages':pages,
            'source_file':relative,'source_checksum':checksum,'source':path.name}


def manifest():
    return json.loads((settings.BASE_DIR / 'knowledge/corpus/manifest.json').read_text(encoding='utf-8'))


def source_unchanged(document):
    if not document.source_file:
        return True  # Explicit text fixtures used by focused tests/evaluation.
    try:
        return file_digest(corpus_path(document.source_file)) == document.source_checksum
    except (ValueError,OSError):
        return False
