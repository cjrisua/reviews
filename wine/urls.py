from django.urls import include,path
from rest_framework.routers import SimpleRouter
from . import views
from django.urls import reverse_lazy

app_name = 'wine'
router = SimpleRouter()
router.register(
    prefix=r'',
    basename='wines',
    viewset=views.WineDocumentViewSet
)
#urlpatterns = router.urls


urlpatterns = [
    #path('<slug:producer>/<str:year>/<slug:winename>/', views.wine_detail, name='wine_detail'),
    path('register/', views.register, name='wine_register'),
    path('dashboard/', views.Dashboard.as_view(), name='wine_dashboard'),
    path(r'inventory/<section>/', views.inventory, name='inventory'),
    path(r'inventory/terroir/add/', views.TerroriCreateView.as_view(success_url=reverse_lazy('wine:wine_dashboard'), success_message = "Saved!"), name='inventory_terroir_add'),
    path('',include(router.urls)),
]