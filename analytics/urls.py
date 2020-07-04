from django.conf.urls import url
from . import views
app_name='analitycs'
urlpatterns = [
    url(r'^displacy/<int:wine_id>/$', views.displacy_detail, name='displacy_detail'),
]