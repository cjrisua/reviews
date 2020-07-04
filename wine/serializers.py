from .models import Producer, Wine, Critic, Market, Review
from rest_framework import serializers
from .analytics.wineentities import WineEntities

class CriticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Critic
        fields = ['name']

class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ['name']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['score','issuedate','observation','critic']

class MarketSerializer(serializers.ModelSerializer):
    #reviews = ReviewSerializer(many=True)
    class Meta:
        model = Market
        fields = ['year','price']

    def create(self, validated_data):
        market = Market.objects.create(**validated_data)
        return market

class WineSerializer(serializers.ModelSerializer):
    vintage = MarketSerializer(many=True)
    class Meta:
        model = Wine
        fields = ['name','country','region','terroir','vintage']

    def create(self, validated_data):
        wine = Wine.objects.create(**validated_data)
        return wine

class WineReviewSerializer(serializers.ModelSerializer):
    wines = WineSerializer(many=True)
    enities = WineEntities()
    class Meta:
        model = Producer
        fields = ['name','wines']
        
    def create(self, validated_data):
        wines_data = validated_data.pop('wines')
        producer, created = Producer.objects.get_or_create(**validated_data)
        for wine_data in wines_data:
            vintage_data = wine_data.pop('vintage')[0]
            self.enities.ReadEntities(wine_data["name"])
            wine, created = Wine.objects.get_or_create(producer=producer, **wine_data)
            market, created = Market.objects.get_or_create(wine=wine, **vintage_data)
        return producer

class ProducerWinesSerializer(serializers.ModelSerializer):
    wines = WineSerializer(many=True)
    class Meta:
        model = Producer
        fields = ['name','wines']
    
    def create(self, validated_data):
        wines_data = validated_data.pop('wines')
        producer = Producer.objects.create(**validated_data)
        for wine_data in wines_data:
            vintage_data = wine_data.pop('vintage')[0]
            wine = Wine.objects.create(producer=producer, **wine_data)
            Market.objects.create(wine=wine, **vintage_data)
        return producer

    def update(self, instance, validated_data):
        producer_mapping = {producer.id: producer for producer in instance}
        return []