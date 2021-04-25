from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from ..models import Market, VarietalBlend, Wine, Producer, Terroir

# Name of the Elasticsearch index
INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])
print(INDEX)
# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
) 

#@INDEX.doc_type
class WineDocument(Document):
    id = fields.IntegerField(attr='id')
    winename = fields.TextField(attr='wine_indexing')
    terroir = fields.TextField(attr='region_indexing')
    vintages = fields.TextField(attr='vintages_indexing')

    class Django:
        model = Wine