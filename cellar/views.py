from django.shortcuts import render
from .models import Collection

def cellar_list(request):
    wine_collection = Collection.objects.all()
    return render( request, 
                   'cellar/collection/list.html',
                   {'collection': wine_collection})

