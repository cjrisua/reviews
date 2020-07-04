from django.contrib import admin
from wine.models import Wine, Producer, Market, Critic, Review

admin.site.register(Producer)
admin.site.register(Market)
admin.site.register(Critic)

@admin.register(Review)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('critic','marketitem','score','issuedate')

@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
     list_display = ('producer','name','country','region')
     list_filter = ( 'country', 'region')
     search_fields = ('producer', 'name')
