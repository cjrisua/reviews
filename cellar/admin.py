from django.contrib import admin
from cellar.models import Cellar, Curator, Collection, Location
#@admin.register(Cellar)
# Register your models here.
admin.site.register(Curator)
admin.site.register(Location)


@admin.register(Cellar)
class CellarAdmin(admin.ModelAdmin):
    list_display = ('name','admin','capacity')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collectible','cellar',)
