from django.apps import apps
from django.views.generic.list import ListView

sidebar_inventory=[
    {'id':'producer','name':'Producers', 'url':'producer'},
    {'id':'region','name':'Wine Regions','url':'region'},
    {'id':'wine','name':'Wines','url':'wine'},
    {'id':'varietalblend','name':'Varietal','url':'varietalblend'},
    {'id':'vintage','name':'Vintage Chart','url':'vintage'},
    {'id':'vintageregion','name':'Vintage Region','url':'vintage-region'}
]
def getInventory(sections):
    result = []
    section_info = {}
    if type(sections) == str:
        sections = [sections]

    for section in sections:
        Model = apps.get_model('wine', section)
        section_info = { 
                    'name' : [s['name'] for s in sidebar_inventory if s.get('id') == section][0],
                    'count':  Model.objects.count(),
                    'section':[s['url'] for s in sidebar_inventory if s.get('id') == section][0],
                    'search' : 'ON'
                    }
        result.append(section_info)
    return result