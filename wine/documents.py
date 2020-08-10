from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Document, Index, fields 
from django_elasticsearch_dsl.registries import registry

from .models import Wine

wine_index = Index('wines')
wine_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
) 

@registry.register_document
class WineDocument(Document):

    id = fields.IntegerField(attr='id')

    name = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
        }
    )
    review = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
        }
    )
    producer = fields.IntegerField(attr='producer_id')

    class Django:
        model = Wine
    
    class Index:
        name = "wine"