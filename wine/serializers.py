from .models import Producer, Wine, Critic, Market, Review
from rest_framework import serializers

class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ['name']
class MarketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Market
        fields = ['year','price']

class WineSerializer(serializers.ModelSerializer):
    vintage = MarketSerializer(many=True)
    class Meta:
        model = Wine
        fields = ['name','country','region','terroir','vintage']

    def create(self, validated_data):
        wine = Wine.objects.create(**validated_data)
        return wine

class CriticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Critic
        fields = ['name']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['score','issuedate','observation','critic']

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