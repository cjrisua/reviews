from .models import (Producer, Wine, Critic,
                    Market, Review, Terroir, Country, Varietal,
                    Vintage, MasterVarietal, VarietalBlend, Region, VintageRegion)
from rest_framework import serializers
from .analytics.wineentities import WineEntities
from .documents.wine import WineDocument
from .documents.producer import ProducerDocument
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework.response import Response


class WineDocumentSerializer(DocumentSerializer):
    class Meta:
        document = WineDocument
        fields = (
            'id',
            'winename',
            'vintages',
            'review',
            'varietal',
            'terroir',
        )


class ProducerDocumentSerializer(DocumentSerializer):

    class Meta:
        document = ProducerDocument
        fields = (
            'id',
            'producer',
            'wine',
            'vintage',
        )


class MasterVarietalSerializer(serializers.ModelSerializer):
        class Meta:
            model = MasterVarietal
            fields = ['id', 'name', 'slug']
            lookup_field = 'slug'


class VarietalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Varietal
        fields = ['id', 'name', 'slug']
        lookup_field = 'slug'


class VarietalBlendSerializer(serializers.ModelSerializer):
    #mastervarietal_id = serializers.PrimaryKeyRelatedField(source='mastervarietal', read_only=True)
    mastervarietal_name = serializers.StringRelatedField(source='mastervarietal',read_only=True)

    class Meta:
        model = VarietalBlend
        fields = ['id', 'mastervarietal', 'varietal','mastervarietal_name']
        lookup_field = 'id'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'abbreviation', 'slug', 'productionrank']
        lookup_field = 'slug'


class TerroirListSerializer(serializers.ListSerializer):
      def update(self, instance, validated_data):
        terroir_mapping = {terroir.id: terroir for terroir in instance}
        data_mapping = {item['id']: item for item in validated_data}
        # Perform creations and updates.
        ret = []
        for terroir_id, data in data_mapping.items():
            terroir = terroir_mapping.get(terroir_id, None)
            if terroir is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(terroir, data))
        # Perform deletions.
        for terroir_id, terroir in data_mapping.items():
            if terroir_id not in data_mapping:
                terroir.delete()
        return ret
class RegionSerializer(serializers.ModelSerializer):
     country_name = serializers.StringRelatedField(source='country',read_only=True)
     country_slug = serializers.SlugRelatedField(source='country',read_only=True, slug_field='slug')
     class Meta:
        model = Region
        fields = ['id','country','name','region','slug', 'country_name','country_slug']

class TerroirSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    country_name = serializers.StringRelatedField(source='country',read_only=True)
    traverse = serializers.StringRelatedField(source='region_traverse',read_only=True)
    with_subterroir = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Terroir
        fields = ['id','name', 'parentterroir', 'isappellation', 'isvineyard','country_name','country','traverse','with_subterroir','isunknown']
        list_serializer_class = TerroirListSerializer

    def create(self, validated_data):
         terroir, created = Terroir.objects.get_or_create(**validated_data)
         return terroir
    
    def update(self, instance, validated_data):
        print(validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.isvineyard = validated_data.get('isvineyard', instance.isvineyard)
        instance.isappellation = validated_data.get('isappellation', instance.isappellation)
        instance.parentterroir = validated_data.get('parentterroir', instance.parentterroir)
        instance.isunknown = validated_data.get('isunknown', instance.isunknown)
        try:
            instance.save()
        except Exception as inst:
            print(inst)
        return instance
    
    def delete(self, instance):
        print("delete " + instance)
        return instance

class VintageRegionSerializer(serializers.ModelSerializer):
    region = RegionSerializer(many=True)
    class Meta:
        model = VintageRegion
        fields = ['id','name','slug','region']

class VintageChartSerializer(serializers.ModelSerializer):
    region = VintageRegionSerializer()
    varietal = VarietalBlendSerializer()
    country_name = serializers.StringRelatedField(source='country',read_only=True)
    region_name = serializers.StringRelatedField(source='region',read_only=True)
    mastervarietal_name = serializers.StringRelatedField(source='mastervarietal',read_only=True)
    class Meta:
        model = Vintage
        fields = '__all__'
        ordering=['region_name']


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
        fields = ['producer','varietal','terroir','name','id']

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
