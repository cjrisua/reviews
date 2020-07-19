from django.shortcuts import render
from .models import Collection
from .serializers import CollectionSerializer
from rest_framework import viewsets
from django.views import View
from django.views.generic.list import ListView

class CollectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Collection.objects.order_by('-collectible')
    serializer_class = CollectionSerializer

class CollectionListView(ListView):
    #module = Collection
    template_name = 'cellar/collection/list.html'
    queryset = Collection.objects.all()
    context_object_name ='collection'

    #def get_queryset(self):
    #    return Collection.objects.filter(id=3)

"""
def cellar_list(request):
    wine_collection = Collection.objects.all()
    return render( request, 
                   'cellar/collection/list.html',
                   {'collection': wine_collection})

"""