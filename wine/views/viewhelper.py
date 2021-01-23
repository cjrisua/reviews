from django.apps import apps

sidebar_inventory=[
    {'id':'producer','name':'Producers'},
    {'id':'terroir','name':'Wine Regions'},
    {'id':'wine','name':'Wines'},
    {'id':'varietalblend','name':'Varietal'}
]
def getInventory(section):
     Model = apps.get_model('wine', section)
     return [{'name' : [s['name'] for s in sidebar_inventory if s.get('id') == section][0],
                    'count':  Model.objects.count(),
                    'section':section,
                    'search' : 'ON'
                    }]