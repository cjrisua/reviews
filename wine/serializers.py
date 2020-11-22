from .models import (Producer, Wine, Critic, 
                    Market, Review, Terroir, Country, Varietal,
                    MasterVarietal, VarietalBlend)
from rest_framework import serializers
from .analytics.wineentities import WineEntities
from .documents.wine import WineDocument
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework.response import Response

class WineDocumentSerializer(DocumentSerializer):
    class Meta:
        document = WineDocument
        fields = (
            'winename',
            'vintages',
            'review',
            'varietal',
        )
class MasterVarietalSerializer(serializers.ModelSerializer):
        class Meta:
            model = MasterVarietal
            fields = ['id','name','slug']
            lookup_field ='slug'

class VarietalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Varietal
        fields = ['id','name','slug']
        lookup_field ='slug'

class VarietalBlendSerializer(serializers.ModelSerializer):
    #mastervarietal_id = serializers.PrimaryKeyRelatedField(source='mastervarietal', read_only=True)
    class Meta:
        model = VarietalBlend
        fields = ['id','mastervarietal','varietal']
        lookup_field ='id'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','name','abbreviation','slug','productionrank']
        lookup_field ='slug'

class TerroirSerializer(serializers.ModelSerializer):
    country_name = serializers.StringRelatedField(source='country',read_only=True)
    traverse = serializers.StringRelatedField(source='region_traverse',read_only=True)
    class Meta:
        model = Terroir
        fields = ['id','name', 'parentterroir', 'isappellation', 'isvineyard','country_name','country','traverse']
        #lookup_field = 'slug'

    def create(self, validated_data):
         terroir, created = Terroir.objects.get_or_create(**validated_data)
         return terroir
    
    def update(self, instance, validated_data):
        print(self.context['request'].data)
        print(validated_data)
        #if self.context['request'].method == "PUT":
        #   pass
        #elif self.context['request'].method == "PATCH":
        instance.name = validated_data.get('name', instance.name)
        instance.isvineyard = validated_data.get('isvineyard', instance.isvineyard)
        instance.isappellation = validated_data.get('isappellation', instance.isappellation)
        instance.parentterroir = validated_data.get('parentterroir', instance.parentterroir)
        instance.save()
        return instance
    
    def delete(self, instance):
        print("delete " + instance)
        return instance

class CriticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Critic
        fields = ['name']

class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ['id','name','slug']
        

class ReviewSerializer(serializers.ModelSerializer):
    critic = CriticSerializer(many=True)
    #marketitem = MarketSerializer(many=False)

    class Meta:
        model = Review
        fields = ['critic','issuedate','observation','score']

    def create(self, validated_data):
        review = Review.objects.create(**validated_data)
        return review

class MarketSerializer(serializers.ModelSerializer):
    #observations = ReviewSerializer(many=True)

    class Meta:
        model = Market
        fields = ['id','year','price']

    def create(self, validated_data):
        market = Market.objects.create(**validated_data)
        return market

class WineSerializer(serializers.ModelSerializer):
    #producer = ProducerSerializer(many=False)
    #terroir = TerroirSerializer(many=False)
    #varietal = MasterVarietalSerializer(many=False)
    
    class Meta:
        model = Wine
        fields = ['producer','varietal','terroir','name']

    #def create(self, validated_data):
    #    wine = Wine.objects.create(**validated_data)
    #    return wine

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