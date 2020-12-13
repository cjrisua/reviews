from django.contrib import admin
from wine.models import (Varietal, Wine, Producer, Market, 
                         Critic, Review, Terroir, Country, MasterVarietal,
                         VarietalBlend, ProducerWine)

admin.site.register(Producer)
admin.site.register(Market)
admin.site.register(Critic)
admin.site.register(ProducerWine)
#admin.site.register(MasterVarietal)
#admin.site.register(VarietalBlend)

@admin.register(MasterVarietal)
class BelndVarietalAdmin(admin.ModelAdmin):
    list_display = ('id','name','slug',)
    search_fields = ('name',)

@admin.register(VarietalBlend)
class BelndVarietalAdmin(admin.ModelAdmin):
    list_display = ('id','mastervarietal','get_belndvarietal',)
    search_fields = ('mastervarietal__name','varietal__name')

    def get_belndvarietal(self, obj):
        grapes = [grape.name for grape in obj.varietal.all()]
        if len(grapes) > 1:
            return ", ".join(grapes[:-1]) + f" and { grapes[-1:][0]}"
        else:    
            return ", ".join(grapes)

@admin.register(Varietal)
class VarietalAdmin(admin.ModelAdmin):
    list_display = ('id','name','slug',)
    list_filter = ( 'name',)
    search_fields = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id','abbreviation','name','productionrank')
    list_filter = ( 'name',)
    search_fields = ('name',)


@admin.register(Terroir)
class TerroirAdmin(admin.ModelAdmin):
    list_display = ('name','get_terroirs','isappellation','isvineyard','country')
    list_filter = ( 'country',)
    search_fields = ('parentterroir__name','name')

    def __init__(self, model, admin_site):
        self.__terroirs = []
        super().__init__(model, admin_site)
        
    def parentterroirs(self, terroir):
        if terroir is not None:
            self.__terroirs.append(terroir.name)
            if terroir.parentterroir is not None:
                self.parentterroirs(terroir.parentterroir)

    def get_terroirs(self, obj):
        self.__terroirs = []
        self.parentterroirs(obj.parentterroir)
        if len(self.__terroirs) > 1:
            return " > ".join(self.__terroirs[::-1])
        elif len(self.__terroirs) == 1:
            return self.__terroirs[0]
        else:
            return obj.name

@admin.register(Review)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('critic','marketitem','score','issuedate',)

@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
    

    list_display = ('producer','name','get_terroirs',)
    list_filter = ( 'terroir', )
    search_fields = ('producer', 'name','get_terroirs',)

    def __init__(self, model, admin_site):
        self.__terroirs = []
        super().__init__(model, admin_site)

    def parentterroirs(self, terroir):
        self.__terroirs.append(terroir.name)
        if terroir.parentterroir is not None:
            self.parentterroirs(terroir.parentterroir)

    def get_terroirs(self, obj):
        self.__terroirs = []
        self.parentterroirs(obj.terroir)
        if len(self.__terroirs) > 1:
            return " > ".join(self.__terroirs[::-1])
        else:
            return self.__terroirs[0]