"""Load only the named synthetic corpus. Never reset accounts or rewrite existing docs."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from knowledge.models import Document
from knowledge.pdf_sources import extract_pdf, manifest

class Command(BaseCommand):
    help = 'Extract clean source PDFs into documents; --poison includes attack PDFs. Indexing is a separate student step.'
    def add_arguments(self,parser):
        parser.add_argument('--poison',action='store_true')
        parser.add_argument('--refresh',action='store_true',help='Re-extract changed PDFs and increment source revision; does not build vectors or change approval/ownership.')
        parser.add_argument('--approve-lab-injection',action='store_true',help='Explicitly approve only the synthetic injection to test runtime defense after provenance repairs.')
    def handle(self,*args,**options):
        from django.db import transaction
        groups = {'clean','poisoned'} if options['poison'] else {'clean'}
        # Extract every selected file before any database changes, so a broken
        # PDF cannot leave a partially imported corpus.
        prepared = []
        for row in manifest():
            if row['group'] not in groups:
                continue
            try:
                extracted = extract_pdf(row['file'])
            except Exception as exc:
                raise CommandError(f"Could not extract {row['file']}: {exc}") from exc
            owner = None
            if row.get('owner'):
                owner = get_user_model().objects.filter(username=row['owner']).first()
                if owner is None:
                    raise CommandError('Run seed_demo first; private PDFs require their named owner.')
            prepared.append((row,extracted,owner))
        with transaction.atomic():
            for row,extracted,owner in prepared:
                extracted = {**extracted,'title':row['title']}
                defaults = {k:row[k] for k in ('title','visibility','approved')}
                defaults.update(extracted,owner=owner)
                doc,created = Document.objects.get_or_create(slug=row['slug'],defaults=defaults)
                status = 'extracted' if created else 'preserved'
                refresh = not created and options['refresh'] and any(
                    getattr(doc, key) != value for key, value in extracted.items()
                )
                if refresh:
                    for key,value in extracted.items():
                        setattr(doc,key,value)
                    doc.revision += 1
                    doc.save()
                    status = 'refreshed; reindex required'
                self.stdout.write(f"{doc.slug}: {status} ({len(doc.source_pages)} PDF pages)")
        if options['approve_lab_injection']:
            updated = Document.objects.filter(slug='it-bulletin-2026-17').update(approved=True)
            if not updated:
                raise CommandError('Add the lab injection first with --poison.')
            self.stdout.write('Synthetic injection approved for the runtime exercise. This is not a production approval procedure.')
