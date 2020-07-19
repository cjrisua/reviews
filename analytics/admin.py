from django.contrib import admin
from .models import ParkerSomm

@admin.register(ParkerSomm)
class ParkerSommAdmin(admin.ModelAdmin):
    list_display = ('keywords','metadata','sourceid','sourcetype')
