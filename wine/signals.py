from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django_elasticsearch_dsl.registries import registry

@receiver(post_save)
def update_document(sender, **kwargs):
    print("update_document")
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']

    if app_label == 'wine':
        if model_name == 'market':
            #instances = instance.wines.all()
            registry.update(instance.wine)
            #for _instance in instances:
            #    registry.update(_instance)

@receiver(post_delete)
def delete_document(sender, **kwargs):
    print('delete_document')
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']

    if app_label == 'wine':
        if model_name == 'market':
            registry.update(instance.wine)
            #instances = instance.wine.all()
            #for _instance in instances:
            #    registry.update(_instance)