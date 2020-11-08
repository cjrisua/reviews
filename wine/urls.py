from django.urls import include,path
from rest_framework.routers import SimpleRouter
from . import views

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
    path('',include(router.urls)),
]