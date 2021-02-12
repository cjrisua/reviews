from django import template
from wine.models import Terroir,Region

register = template.Library()

@register.filter(name='child_count')
def region_traverse(value):
    return Region.objects.filter(region_id=value).count()

@register.filter(name='region_traverse')
def region_traverse(value):
    return get_region(Region.objects.filter(pk=value)[0])

def subregions(region,regions):
        if region is not None:
            regions.append(region.name)
            if region.region is not None:
                subregions(region.region,regions)

def get_region(region):
        regions = []
        subregions(region.region,regions)
        if len(regions) > 1:
            return " > ".join(regions[::-1])
        elif len(regions) == 1:
            return regions[0]
        else:
            return region.name

@register.inclusion_tag('wine/region/region_treeview.html')
def region_treeview():
    return {'regions' :  Region.objects.filter(region__isnull=True)}
    
    #html = ""
    #for t in Terroir.objects.filter(parentterroir__isnull=True):
    #    html += f'<li id="{t.id}"><i class="fas fa-angle-right rotate wr-is-clickable"></i><span><i class="far fa-globe ic-w mx-1 draggable" draggable="true"></i><span class="droppable"><a href="#" class="click-region-name">{t.name}</a></span></span><ul class="nested"></ul></li>'
    #return html