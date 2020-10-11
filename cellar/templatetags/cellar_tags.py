from django import template
from wine.models import Producer

register = template.Library()

@register.simple_tag
def producer_dict():
    producers = Producer.objects.all()
    results = [ {
                 "id":p.id,
                 "name":p.name
                 } 
                 for p in producers]
    return results