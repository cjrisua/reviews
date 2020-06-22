from .models import Producer, Wine, Critic, Market, Review
from rest_framework import serializers

class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ['name']

class WineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = ['name','country','region','terroir','producer']

class CriticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Critic
        fields = ['name']

class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ['releaseprice','vintage','reviews', 'wine']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['score','issuedate','observation','critic','market']

class ProducerWinesSerializer(serializers.ModelSerializer):
    #wines = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    wines = WineSerializer(many=True, read_only=True)
    class Meta:
        model = Producer
        fields = ['name','wines']