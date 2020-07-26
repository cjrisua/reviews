from .models import BlendVarietal,  Producer, Wine, Critic, Market, Review, Terroir, Country, Varietal
from rest_framework import serializers
from .analytics.wineentities import WineEntities

class VarietalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Varietal
        fields = ['id','name','slug']
        lookup_field ='slug'


class BlendVarietalSerializer(serializers.ModelSerializer):
    #varietal = VarietalSerializer(many=True)

    class Meta:
        model = BlendVarietal
        fields = ['id','name','varietal']
        lookup_field ='id'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','name','abbreviation','slug']
        lookup_field ='slug'

class TerroirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terroir
        fields = ['id','name', 'parentterroir', 'isappellation', 'isvineyard']
        lookup_field = 'slug'

    def create(self, validated_data):
         terroir, created = Terroir.objects.get_or_create(**validated_data)
         return terroir

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

    def create(self, validated_data):
        review = Review.objects.create(**validated_data)
        return review

class MarketSerializer(serializers.ModelSerializer):
    observations = ReviewSerializer(many=True)

    class Meta:
        model = Market
        fields = ['id','year','price','observations']

    def create(self, validated_data):
        market = Market.objects.create(**validated_data)
        return market

class WineSerializer(serializers.ModelSerializer):
    vintage = MarketSerializer(many=True)
    
    class Meta:
        model = Wine
        fields = ['name','terroir','vintage']

    def create(self, validated_data):
        wine = Wine.objects.create(**validated_data)
        return wine

class WineReviewSerializer(serializers.ModelSerializer):
    wines = WineSerializer(many=True)
    enities = WineEntities()
    class Meta:
        model = Producer
        fields = ['id','name','wines']
        
    def create(self, validated_data):
        wines_data = validated_data.pop('wines')
        producer, created = Producer.objects.get_or_create(**validated_data)
        for wine_data in wines_data:
            vintage_data = wine_data.pop('vintage')[0]
            self.enities.ReadEntities(wine_data["name"])
            wine, created = Wine.objects.get_or_create(producer=producer, **wine_data)
            
            reviews = vintage_data.pop('observations')

            market, created = Market.objects.get_or_create(wine=wine, **vintage_data)

            for review_data in reviews:
                review, created = Review.objects.get_or_create(marketitem=market, **review_data)

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