from django.core.management.base import BaseCommand
from ...models import Producer,Wine, Market, Terroir
import pandas as pd
from django.utils.text import slugify 
class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        #score,observation,releasedprice,country,region,issuedate
        df  = pd.read_csv("winespectator.csv")

        terroir = Terroir.objects.all()

        for name, group in df.groupby('house'):
            producer, created = Producer.objects.get_or_create(slug=slugify(name), defaults={'name': name})
            for wine in group.iloc():
                print(f"producer: {producer.id}")
                
                exit()