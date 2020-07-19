from .models import ParkerSomm
from rest_framework import serializers

class ParkerSommSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkerSomm
        fields = ['id','keywords','metadata','sourceid','sourcetype']