from django.contrib import admin
from wine.models import Wine, Producer, Market, Critic, Review

admin.site.register(Producer)
admin.site.register(Wine)
admin.site.register(Market)
admin.site.register(Critic)

@admin.register(Review)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('critic','marketitem','score','issuedate')