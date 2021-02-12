from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from wine.views.viewhelper import getInventory
from wine.views.filters import FilteredListView,RegionFilter

from rest_framework import viewsets
from ..serializers import RegionSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django_elasticsearch_dsl_drf.filter_backends import (
        FacetedSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
        GeoSpatialFilteringFilterBackend,
        GeoSpatialOrderingFilterBackend,
        NestedFilteringFilterBackend,
        DefaultOrderingFilterBackend,
        SuggesterFilterBackend,
        IdsFilterBackend,
        CompoundSearchFilterBackend,
        SimpleQueryStringSearchFilterBackend,
)

from wine.forms import RegionForm
from wine.models import Region, Country, Region

from django.views.generic.list import ListView
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView
from django.db.models import Count
section = 'region'

class HomePageView(ListView):
    model = Region
    template_name = "wine/region/home.html"
    context_object_name = 'regions'
    queryset = Region.objects.values('country__name', 'country__slug') \
               .annotate(country_region_count=Count('country')) \
               .order_by('-country__name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory'] = getInventory(section)
        return context

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    lookup_field = 'slug'
    filterset_fields = ['region']
    search_fields = ['slug']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]


class RegionCreateView(SuccessMessageMixin, CreateView):
    #template_name = 'wine/region/create.html'
    #form_class = RegionForm
    success_message = "%(name)s was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        #country_init = Country.objects.order_by().values_list('country__id','country__name').distinct()
        self.__initial = {}
        countriesqs = Country.objects.order_by().values_list('id','name').distinct().order_by('-name')
        self.__initial['country'] = countriesqs
        if self.kwargs.get('country',None):
            self.__initial['choice_initial_id'] = countriesqs.get(slug=self.kwargs['country'])
        if self.kwargs.get('region',None):
            region = Region.objects.get(country__slug=self.kwargs['country'],
                    slug=self.kwargs['region'])
            self.__initial['region'] = region.name
            self.__initial['region_hidden'] = region.id
            self.__initial['choice_initial_id'] = (region.country.id,region.country.name)
            
        return super().dispatch(*args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        
        #country_init = Region.objects.order_by().values_list('country__id','country__name').distinct()
        context = {'form': RegionForm(request.POST, initial=self.__initial)}
        if context['form'].is_valid():
            context['form'].save()
            params={}
            if context['form'].result:
                params = {'country': context['form'].result.country.slug}
                if context['form'].result.region is not None:
                    params['region']=context['form'].result.region.slug
            return HttpResponseRedirect(reverse_lazy('wine:region_country', kwargs=params))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/region/create.html', context)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': RegionForm(initial=self.__initial)}
        return render(request, 'wine/region/create.html', context)


class RegionUpdateView(SuccessMessageMixin, UpdateView):
    success_message = "%(name)s was updated successfully"
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        r = Region.objects.get(country__slug=self.kwargs['country'],slug=self.kwargs['region'])
        country_init = Region.objects.order_by().values_list('country__id','country__name').distinct()
        self.initial={
            'id' : r.id,
            'country' : country_init,
            'name' : r.name,
            'region' : r.region,
            'region_hidden' : r.region.id if r.region is not None else None,
            'choice_initial_id' : (r.country.id, r.country.name)
        }
        return super().dispatch(*args, **kwargs)
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = {'form': RegionForm(request.POST, initial=self.initial)}
        if context['form'].is_valid():
            context['form'].save()
            params={}
            if context['form'].result:
                params = {'country': context['form'].result.country.slug}
                if context['form'].result.region is not None:
                    params['region']=context['form'].result.region.slug
            return HttpResponseRedirect(reverse_lazy('wine:region_country', kwargs=params))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/region/update.html', context)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': RegionForm(initial=self.initial,request=kwargs)}
        return render(request, 'wine/region/update.html', context)

class RegionListView(ListView):
    model = Region
    paginate_by = 25
    context_object_name = 'regions'
    template_name = 'wine/region/list.html'
    ordering = ['-name']
    
    def get_queryset(self):
        qs = None
        filters={}
        for q in self.kwargs.items():
            if q[0]=='country':
                filters['country__slug']=q[1]
            if q[0]=='region':
                filters['region__slug']=q[1] #sub regions with
        #your_filters = { 'field_1__exact': value_1, 'field_2__gte': value_2}
        if 'region__slug' not in filters:
            filters['region']=None

        '''
        #qs = None
        if self.kwargs.get('pk',None) and self.kwargs.get('country',None):
            qs = Region.objects.filter(country__slug=self.kwargs['country'], parentregion=self.kwargs['pk'])
        elif self.kwargs.get('country',None):
            qs = Region.objects.filter(country__slug=self.kwargs['country'], parentregion=None)
        elif self.kwargs.get('pk',None):
            region = Region.objects.filter(parentregion=self.kwargs['pk'])
            #if region.count() == 0:
            #    return Region.objects.filter(id=self.kwargs['pk'])
            qs = region
        elif self.request.GET.get('name', None):
            region = Region.objects.filter(name__icontains=self.request.GET['name'])
            #result = [(t,Region.objects.filter(parentregion=t.id).count()) for t in region]
            #result.sort(key = lambda x: -x[1])
            #qs = [r[0] for r in result]
            qs = region
        else:  
            qs = Region.objects.filter(parentregion=None)

        if self.request.GET.get('isunknown',None) and self.request.GET['isunknown'] != 'true':
            qs = qs.exclude(isunknown=True)
            
        '''
        #return Region.objects.all()
        if bool(filters):
            return Region.objects.filter(**filters).order_by('name')
        else:
            return Region.objects.all().order_by('name')
        #return result.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('region',None):
            if len(context['regions']) != 0:
                context['region'] = context['regions'][0].region
            else:
                context['region'] =  Region.objects.get(
                    country__slug=self.kwargs['country'],
                    slug=self.kwargs['region'])

            context['iscountry'] = False
        elif len(context['regions']) > 0:
             context['region'] = { 'name':context['regions'][0].country.name,
                                   'slug':None,
                                   'id': 0,
                                   'region':0,
                                   'country':{'slug':context['regions'][0].country.slug}}
             context['iscountry'] = True
        context['inventory'] = getInventory(section)
        return context