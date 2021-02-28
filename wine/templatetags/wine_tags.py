from django import template
from wine.models import Terroir,Region

register = template.Library()

@register.filter(name='is_in')
def is_in(value,args):
    year = [k for k in value.split('-')][1]
    varietal = [k for k in value.split('-')][0]
    result = [{'year':f['year'],'score':f['score']} for x in args for f in x.list if f['year'] == year and f['varietal']['mastervarietal_name'] == varietal]
    if len(result) > 0:
        return result[0]['score']
    else:
        return '0'
@register.filter(name='point_scoring')
def point_scoring(value,args):
    if args == 0:
        return 'VNS'
    else:
        return f"{'' if args-value > 0 else '+' if args-value < 0 else ''}{int(args-value)}"
@register.filter(name='vintage_score')
def vintage_score(value,args):
    score =  0 if not args.filter(year=value).exists() else args.get(year=value).score
    if score == 0:
        return 0
    else:
        return score

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