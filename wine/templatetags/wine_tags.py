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

@register.inclusion_tag('wine/terroir/terroir_treeview.html')
def terroir_treeview():
    return {'terroirs' :  Terroir.objects.filter(parentterroir__isnull=True)}
    
    #html = ""
    #for t in Terroir.objects.filter(parentterroir__isnull=True):
    #    html += f'<li id="{t.id}"><i class="fas fa-angle-right rotate wr-is-clickable"></i><span><i class="far fa-globe ic-w mx-1 draggable" draggable="true"></i><span class="droppable"><a href="#" class="click-region-name">{t.name}</a></span></span><ul class="nested"></ul></li>'
    #return html