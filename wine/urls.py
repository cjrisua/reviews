from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

app_name = 'wine'
router = SimpleRouter()
router.register(
    prefix=r'',
    basename='wines',
    viewset=views.WineDocumentViewSet
)
urlpatterns = router.urls

"""
urlpatterns = [
    path('<slug:producer>/<str:year>/<slug:winename>/', views.wine_detail, name='wine_detail'),
]
"""