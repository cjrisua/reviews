from django.core.management.base import BaseCommand
from ...models import Producer
import pandas as pd
from django.utils.text import slugify 
class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        producer = Producer.objects.all()
        print(f"Total producers: {len(producer)}")
        df  = pd.read_csv("winespectator.csv")
        print(f"Dataset Size {df.shape[0]}")
        for name, group in df.groupby('house'):
            producer, created = Producer.objects.get_or_create(slug=slugify(name), defaults={'name': name})
            print(created)