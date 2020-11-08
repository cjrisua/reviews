from django import template
from wine.models import Terroir

register = template.Library()

@register.filter(name='region_traverse')
def region_traverse(value):
    return get_terroirs(Terroir.objects.filter(pk=value)[0])

def parentterroirs(terroir,terroirs):
        if terroir is not None:
            terroirs.append(terroir.name)
            if terroir.parentterroir is not None:
                parentterroirs(terroir.parentterroir,terroirs)

def get_terroirs(terroir):
        terroirs = []
        parentterroirs(terroir.parentterroir,terroirs)
        if len(terroirs) > 1:
            return " > ".join(terroirs[::-1])
        elif len(terroirs) == 1:
            return terroirs[0]
        else:
            return terroir.name