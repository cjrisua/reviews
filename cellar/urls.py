from django.urls import path
from . import views
from wine import views as wineviews
app_name = 'cellar'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('allocation/', views.AllocationListView.as_view(), name='allocation'),
    path('allocation/add/', views.AllocationCreateView.as_view(), name='allocation_create'),
    path('allocation/producer/add/', views.ProducerCreateView.as_view(), name='allocation_producer_create'),
    path('allocation/<int:pk>/', views.AllocationUpdateView.as_view(), name='allocation_update'),
    path('regions/', wineviews.WineRegionsListView.as_view(), name='wine_region'),
    path('regions/<regionid>/', wineviews.WineRegionsListView.as_view(), name='wine_region_detail'),
    path('regions/v2/<regionid>/', wineviews.WineRegions2ListView.as_view(), name='wine_region_list'),
    path('terroir/detail/', wineviews.terrori_detail, name='terroir_detail')
]