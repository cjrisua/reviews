from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
import spacy
from spacy import displacy
from wine.models import Wine
# Create your views here.

def displacy_detail(request, wine_id):
    if request.method == 'GET':
        print(wine_id)
        wine = get_object_or_404(Wine, wine_id=wine_id)
        return HttpResponse("Success!")