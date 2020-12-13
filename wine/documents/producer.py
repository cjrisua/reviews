from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Document, Index, fields, Nested
from django_elasticsearch_dsl_drf.compat import KeywordField, StringField
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from ..models import Market, VarietalBlend, Wine, Producer, Terroir, ProducerWine

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
    filter=[ "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
) 

@INDEX.doc_type
class ProducerDocument(Document):
    id = fields.IntegerField(attr='id')
    producer = fields.TextField(attr='producername_indexing')
    wine = fields.TextField(attr='winename_indexing')
    vintage = fields.TextField(attr='winevintage_indexing')
    #wine = fields.NestedField(attr='winename_indexing')
    # Country object
    '''
    wine = fields.NestedField(
        attr='winename_indexing',
        properties={
            'name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }
            ),
            'vintages': fields.ObjectField(
                properties={
                    'vintage': StringField(
                        #analyzer=html_strip,
                        fields={
                            'raw': KeywordField(),
                        },
                    ),
                },
            ),
        },
    )'''
    #wineattributes = fields.ObjectField(properties={
    #        'winename' :  fields.TextField(attr='winename_indexing'),
    #        'vintages' : fields.TextField(attr='vintages_indexing')
    #    }
    #)

    class Django:
        model = ProducerWine
