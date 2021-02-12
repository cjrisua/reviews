from django.urls import include,path
from rest_framework.routers import SimpleRouter
from . import views
from django.urls import reverse_lazy

app_name = 'wine'
router = SimpleRouter()
router.register(prefix=r'w',basename='wines',viewset=views.WineDocumentViewSet)
router.register(prefix=r'p',basename='producers',viewset=views.ProducerDocumentViewSet)
#urlpatterns = router.urls


urlpatterns = [
    #path('<slug:producer>/<str:year>/<slug:winename>/', views.wine_detail, name='wine_detail'),
    path('register/', views.WineRegisterView.as_view(), name='wine_register'),
    path('dashboard/', views.Dashboard.as_view(), name='wine_dashboard'),
    #path(r'inventory/<section>/', views.inventory, name='inventory'),
    path(r'inventory/region/', views.HomePageView.as_view(), name='region-home'),
    path(r'inventory/region/add/', views.RegionCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='region_add'),
    path(r'inventory/region/<slug:country>/add/', views.RegionCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='region_add'),
    path(r'inventory/region/<slug:country>/<slug:region>/add/', views.RegionCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='region_add'),
    path(r'inventory/region/<slug:country>/', views.RegionListView.as_view(), name='region_country'),
    path(r'inventory/region/<slug:country>/<slug:region>/', views.RegionListView.as_view(), name='region_country'),
    path(r'inventory/region/<slug:country>/<slug:region>/update/', views.RegionUpdateView.as_view(), name='region_update'),
    path(r'inventory/region/add/', views.RegionCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='region_add'),
    #path(r'inventory/region/<int:pk>/', views.RegionListView.as_view(), name='region_item'),
    #path(r'inventory/region/<int:pk>/update/', views.RegionUpdateView.as_view(), name='region_update'),
    path(r'inventory/producer/', views.ProducerListView.as_view(), name='producer_list'),
    #path(r'inventory/producer/add/', views.ProducerCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='inventory_producer_add'),
    #path(r'inventory/terroir/add/', views.TerroriCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='inventory_terroir_add'),
    path(r'inventory/varietalblend/add/', views.VarietalBlendCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard')), name='inventory_varietalblend_add'),
    path(r'inventory/varietalblend/<int:pk>/', views.VarietalBlendUpdateView.as_view(), name='inventory_varietalblend_update'),
    path(r'inventory/wine/', views.WineListView.as_view(), name='wine_list'),
    path(r'inventory/wine/<slug:producer>/', views.WineListView.as_view(), name='wine_list'),
    path(r'inventory/wine/<slug:producer>/<slug:wine>/', views.WineListView.as_view(), name='wine_list'),
    path(r'inventory/wine/<slug:producer>/<slug:wine>/<int:vintage>/detail', views.WineListView.as_view(), name='wine_detail'),
    path(r'inventory/wine/add/', views.WineCreateView.as_view(), name='inventory_wine_add'),
    path(r'inventory/wine/<int:wineid>/vintage/add/', views.WineMarketView.as_view(), name='inventory_wine_vintage_add'),
    #path(r'inventory/wine/<int:vintage>/', views.register, name='inventory_wine_vintage'),
    path('',include(router.urls)),
]