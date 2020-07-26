from django.shortcuts import get_object_or_404, render
from .models import Producer,Wine, Critic, Market, Review, Terroir, Country, Varietal, BlendVarietal
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import BlendVarietalSerializer, ProducerWinesSerializer, WineSerializer, CriticSerializer, MarketSerializer, ReviewSerializer, WineReviewSerializer, TerroirSerializer, CountrySerializer, VarietalSerializer

class BlendVarietalViewSet(viewsets.ModelViewSet):
    queryset = BlendVarietal.objects.all()
    serializer_class = BlendVarietalSerializer
    lookup_field = 'id'

class VarietalViewSet(viewsets.ModelViewSet):
    queryset = Varietal.objects.all()
    serializer_class = VarietalSerializer
    lookup_field = 'slug'

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'slug'

class TerroirViewSet(viewsets.ModelViewSet):
    queryset = Terroir.objects.all()
    serializer_class = TerroirSerializer
    lookup_field = 'slug'

class ProducerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Producer.objects.order_by('-name')
    serializer_class = ProducerWinesSerializer

class WineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Wine.objects.order_by('-name')
    serializer_class = WineSerializer

class CriticViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Critic.objects.order_by('-name')
    serializer_class = CriticSerializer

class MarketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Market.objects.order_by('-vintage')
    serializer_class = MarketSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Review.objects.order_by('-score')
    serializer_class = ReviewSerializer

class WineReviewViewSet(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = WineReviewSerializer

# Create your views here.
def wine_detail(request, producer, year ,winename):
    wine = get_object_or_404(Market, producerslug=producer,
                                     year=year,
                                     wineslug = winename)
    if wine.observations:
        review = Review.objects.filter(marketitem_id=wine.id)

    return render(request,
                  'wine/producer/detail.html',
                  {'wine': wine, 'review' : review})
    #return HttpResponse("return this string")