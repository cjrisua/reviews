from django.core.management.base import BaseCommand
from ...models import Producer, Country
import pandas as pd
from django.utils.text import slugify 

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        countryAlias = [{'United States':['US','United States','USA']}]

        df  = pd.read_csv("terroir.csv")
        print(f"Dataset Size {df.shape[0]}")
        for name, group in df.groupby('country'):
            #producer, created = Producer.objects.get_or_create(slug=slugify(name), defaults={'name': name})
            has_alias = next(filter(lambda x: slugify(name) in [slugify(f) for f in x.values()][0], countryAlias),None)
            country_name = name if has_alias is None else list(has_alias.keys())[0]
            country, created = Country.objects.get_or_create(slug=slugify(name), defaults={'name': name, 'productionrank':0, 'abbreviation':''})
