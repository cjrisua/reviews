from django.core.management.base import BaseCommand
from ...models import Producer, Country
import pandas as pd
from django.utils.text import slugify 

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        countryAlias = [{'United States':['US','United States','USA']}]

        df_terroir  = pd.read_csv("terroir.csv")
        df_country  = pd.read_csv("country_code.csv")

        print(f"Dataset Size {df_terroir.shape[0]}")
        for name, group in df_terroir.groupby('country'):
            #producer, created = Producer.objects.get_or_create(slug=slugify(name), defaults={'name': name})
            has_alias = next(filter(lambda x: slugify(name) in [slugify(f) for f in x.values()][0], countryAlias),None)
            country_name = name if has_alias is None else list(has_alias.keys())[0]
            pd_country = df_country[df_country.Country == country_name]
            country, created = Country.objects.get_or_create(slug=slugify(country_name), 
                    defaults={  'name': name, 
                                'productionrank':pd_country.Rank.values[0], 
                                'abbreviation':pd_country.Alpha3.values[0]})
            
