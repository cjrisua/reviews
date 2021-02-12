from django.core.management.base import BaseCommand
from ...models import Producer, Region, VarietalBlend, MasterVarietal,Wine, Market, Critic, Review
import pandas as pd
from django.utils.text import slugify 
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
from django.db.models import Count
from datetime import datetime

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        producer = Producer.objects.all()
        print(f"Total producers: {len(producer)}")
        df  = pd.read_csv("winespectator.csv")
        print(f"Dataset Size {df.shape[0]}")
        varietal = [n.name.lower() for n in MasterVarietal.objects.all()]
        for name, group in df.groupby('house'):
           producer = Producer.objects.get(slug=slugify(name))
           for row, item in group.iterrows():
                if not re.search('Cabernet Sauvignon', item.terroir, re.IGNORECASE):
                        continue
                #res = any(ele in item['terroir'].lower() for ele in varietal)
                filter_object = list(filter(lambda a:  a.lower() in item['terroir'].lower(), varietal))
                #region = Region.objects.filter().exists()
                fuzzymatches = [ {"id":r.id,"ratio":fuzz.token_set_ratio(item['terroir'],r.name),"name":r.name} for r in Region.objects.filter(country__slug=slugify(item['country']))]
                matches = sorted(fuzzymatches, key = lambda i: i['ratio'],reverse=True)[:3]
                #print(f"{matches[0]['name']}")
                region = Region.objects.get(
                    slug=slugify(matches[0]['name']),
                    country__slug=slugify(item['country']))

                if len(filter_object) == 0:
                    print("filter_object==0")
                elif len(filter_object) == 1:
                    #print(f"{matches[0]['name']}")
                    #print(f"{slugify(filter_object)} {item['terroir']}")
                    blend = VarietalBlend.objects.get(mastervarietal__slug=slugify(filter_object))
                    wine, created = Wine.objects.get_or_create(
                        slug=slugify(item['terroir']), 
                        producer=producer,
                        defaults={'name':item['terroir'],'region':region,'varietal':blend})

                    print(f'wine {wine}')
                    amount=re.findall(r"\$([0-9]+)",item["releasedprice"])
                    market, created = Market.objects.get_or_create(
                            year=item['vintage'],
                            wine=wine,
                            defaults={
                                      'varietal':blend,
                                      'price': amount[0]+'.00' if len(amount) > 0 else + 0.00
                                      })
                    print(f'market {market}')
                    review, created = Review.objects.get_or_create(
                        critic=Critic.objects.get(id=1),
                        marketitem=market,
                        defaults={'observation': item['observation'],
                                  'issuedate': datetime.strptime(item['issuedate'] , '%d-%b-%y'),
                                  'score':item['score']
                                  })
                    print(f'review {review}')
                    market.observations.add(Critic.objects.get(id=1))
                else:
                    print(filter_object)
                    blend = VarietalBlend.objects.filter(varietal__slug__in=filter_object)
                    print(blend)
                '''
                print(list(filter_object))
                if filter_object:
                    region = Region.objects.filter(country__slug=slugify(item['country'])).exists()
                    if not region:
                        print(slugify(item['country']))
                    else:
                        #fuzz.token_set_ratio(item['terroir'],item['terroir'])
                        fuzzymatches = [ {"id":r.id,"ratio":fuzz.token_set_ratio(item['terroir'],r.name),"name":r.name} for r in Region.objects.filter(country__slug=slugify(item['country']))]
                        matches = sorted(fuzzymatches, key = lambda i: i['ratio'],reverse=True)[:3]
                        
                        #wine

                        #print(f"{item['terroir']} | {matches[0]['name']}")
                        #break
                    #break
                    '''