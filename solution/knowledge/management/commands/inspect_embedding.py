from django.core.management.base import BaseCommand
from knowledge.embeddings import embed, model_name

class Command(BaseCommand):
    help = 'Show vector dimensions, a short numeric preview and pairwise cosine similarity.'
    def add_arguments(self,parser):
        parser.add_argument('texts',nargs='+')
    def handle(self,*args,**options):
        vectors = embed(options['texts'])
        self.stdout.write('Embedding model: '+model_name())
        for text,vector in zip(options['texts'],vectors):
            self.stdout.write(f'{text!r}: dimensions={len(vector)}, first_8={vector[:8]}')
        from math import sqrt
        for i in range(1,len(vectors)):
            a,b = vectors[0],vectors[i]
            score = sum(x*y for x,y in zip(a,b))/(sqrt(sum(x*x for x in a))*sqrt(sum(x*x for x in b)))
            self.stdout.write(f'cosine_similarity(text_1,text_{i+1})={score:.5f}')
        self.stdout.write('Similarity is not truth, permission, or a probability. A vector preview is not a word-by-word explanation of meaning.')
