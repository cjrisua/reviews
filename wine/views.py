from .models import Producer,Wine, Critic, Market, Review
from rest_framework import viewsets
from .serializers import ProducerSerializer, WineSerializer, CriticSerializer, MarketSerializer, ReviewSerializer

# Create your views here.

class ProducerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Producer.objects.order_by('-name')
    serializer_class = ProducerSerializer

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