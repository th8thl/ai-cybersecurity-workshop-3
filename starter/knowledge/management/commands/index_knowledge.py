from django.core.management.base import BaseCommand, CommandError
from knowledge.models import Document
from knowledge.ingestion import index_document
from knowledge.embeddings import model_name

class Command(BaseCommand):
    help = 'Embed document passages and upsert reference vectors into the local Chroma index.'
    def add_arguments(self,parser):
        parser.add_argument('--slug',help='Index one document; otherwise index all synthetic knowledge.')
    def handle(self,*args,**options):
        docs = Document.objects.all().order_by('pk')
        if options['slug']:
            docs = docs.filter(slug=options['slug'])
        if not docs.exists():
            raise CommandError('No matching documents. Run seed_knowledge first.')
        for doc in docs:
            self.stdout.write(f'{doc.slug}: {index_document(doc)} passages, model={model_name()}')
