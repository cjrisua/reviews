from django.urls import path
from . import views
app_name = 'cellar'
urlpatterns = [
    path('', views.cellar_list, name='cellar_list'),
]