from django.urls import path
from . import views
app_name = 'wine'
urlpatterns = [
    path('<slug:producer>/<str:year>/<slug:winename>/', views.wine_detail, name='wine_detail'),
    
]