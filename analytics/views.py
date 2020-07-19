from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
import spacy
from spacy import displacy
from wine.models import Wine
from .serializers import ParkerSommSerializer
from .models import ParkerSomm
from rest_framework import viewsets
# Create your views here.

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

nlp = spacy.load("model/")

from rest_framework import mixins
from rest_framework import generics

#class ParkerSommViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows producers to be viewed or edited.
#    """
#    queryset = ParkerSomm.objects.order_by('-id')
#    serializer_class = ParkerSommSerializer

class ParkerSommList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    queryset = ParkerSomm.objects.all()
    serializer_class = ParkerSommSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ParkerSommDetail(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    queryset = ParkerSomm.objects.all()
    serializer_class = ParkerSommSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

"""    
def parkersomm_learn(request):
    if request.method == 'GET':
        return HttpResponse("Get")
    elif request.method == 'POST':
         return HttpResponse("Post")
"""
def displacy_detail(request):
    if request.method == 'GET':
        wineidfilter = request.GET["wine_id"]
        wine  = get_object_or_404(Wine, id=wineidfilter)

        doc = nlp(wine.name)
        return displacy.parse_deps(doc)
    elif request.method == 'POST':
        wineidfilter = request.GET["wine_id"]
        wine  = get_object_or_404(Wine, id=wineidfilter)
        doc = nlp(wine.name)
        return JsonResponse(displacy.parse_ents(doc))