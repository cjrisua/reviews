from django.urls import path
from . import views
from wine import views as wineviews
app_name = 'cellar'
urlpatterns = [
    path('', views.CollectionListView.as_view(), name='cellar'),
    path('regions/', wineviews.WineRegionsListView.as_view(), name='wine_region'),
    path('regions/<regionid>/', wineviews.WineRegionsListView.as_view(), name='wine_region_detail'),
    path('regions/v2/<regionid>/', wineviews.WineRegions2ListView.as_view(), name='wine_region_list'),
    path('terroir/detail/', wineviews.terrori_detail, name='terroir_detail')
]