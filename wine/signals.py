from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
#from .models import ProducerWine
from django_elasticsearch_dsl.registries import registry
from django.apps import apps

@receiver(post_save)
def update_document(sender, **kwargs):
    
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']
    print(f"update_document: {model_name}")
    if app_label == 'wine':
        if model_name == 'market':
            producer_wine = apps.get_model('wine', 'ProducerWine')
            registry.update(producer_wine.objects.get(market_id=instance.id))
            registry.update(instance.wine)

@receiver(pre_delete)
def delete_document(sender, **kwargs):
    print('delete_document')
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']

    if app_label == 'wine':
        if model_name == 'market':
            producer_wine = apps.get_model('wine', 'ProducerWine')
            registry.update(producer_wine.objects.get(market_id=instance.id))
            registry.update(instance.wine)