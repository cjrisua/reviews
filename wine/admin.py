from django.contrib import admin
from wine.models import BlendVarietal, Varietal, Wine, Producer, Market, Critic, Review, Terroir, Country

admin.site.register(Producer)
admin.site.register(Market)
admin.site.register(Critic)


@admin.register(BlendVarietal)
class BelndVarietalAdmin(admin.ModelAdmin):
    list_display = ('name','get_belndvarietal',)
    search_fields = ('varietal','name')

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
    list_display = ('id','abbreviation','name',)
    list_filter = ( 'name',)
    search_fields = ('name',)


@admin.register(Terroir)
class TerroirAdmin(admin.ModelAdmin):
    list_display = ('name','parentterroir','isappellation','isvineyard',)
    list_filter = ( 'name',)
    search_fields = ('name',)

@admin.register(Review)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('critic','marketitem','score','issuedate',)

@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
     list_display = ('producer','name','terroir',)
     list_filter = ( 'terroir', )
     search_fields = ('producer', 'name',)