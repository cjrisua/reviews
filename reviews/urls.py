"""reviews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from wine import views as wineviews
from cellar import views as cellarviews
from analytics import views as analyticsviews
from django.contrib import admin

router = routers.DefaultRouter()
router.register(r'wine', wineviews.WineViewSet)
router.register(r'cellar', cellarviews.CollectionViewSet)
router.register(r'terroir', wineviews.TerroirViewSet)
router.register(r'country', wineviews.CountryViewSet)
router.register(r'varietal', wineviews.VarietalViewSet)
router.register(r'blendvarietal', wineviews.BlendVarietalViewSet)
router.register(r'producer', wineviews.ProducerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('cellar/', include('cellar.urls', namespace='cellar')),
    path('cellar/', cellarviews.CollectionListView.as_view(),name='cellar'),
    path('wine/', include('wine.urls', namespace='wine')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/',  include(router.urls)),
    path('api/learn/<int:pk>/',  analyticsviews.ParkerSommDetail.as_view(), name='analytics'),
    path('api/learn/',  analyticsviews.ParkerSommList.as_view(), name='analytics'),
    #path('wines/', include('wine.urls')),  
]