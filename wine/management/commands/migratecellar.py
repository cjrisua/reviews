from django.core.management.base import BaseCommand
from ...models import Producer,Wine, Market, Terroir
import pandas as pd
from django.utils.text import slugify 
class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        df  = pd.read_csv("MyCellar.csv",encoding='latin1')
        for row, item in df.iterrows():
            vintage = item.Vintage
            producer = item.Producer
            wine = item.Wine