from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
import spacy
from spacy import displacy
from wine.models import Wine
# Create your views here.

nlp = spacy.load("model/")

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