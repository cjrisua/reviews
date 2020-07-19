from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
app_name='analitycs'
urlpatterns = [
    url(r'^displacy/$', views.displacy_detail, name='displacy_detail'),
    url(r'^learn/', views.ParkerSommList.as_view()),
]