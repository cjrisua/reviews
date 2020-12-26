from django.shortcuts import get_object_or_404, render
from .models import (
    MasterVarietal, 
    VarietalBlend, 
    Producer,Wine, 
    Critic, 
    Market, 
    Review, 
    Terroir, 
    Country, 
    Varietal)
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import (  WineDocumentSerializer, 
                            ProducerSerializer, WineSerializer, CriticSerializer, 
                            MarketSerializer, ReviewSerializer, WineReviewSerializer, 
                            TerroirSerializer, CountrySerializer, VarietalSerializer,
                            MasterVarietalSerializer, VarietalBlendSerializer,ProducerDocumentSerializer)
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_EXCLUDE,
    SUGGESTER_COMPLETION,
)
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
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .documents.wine import WineDocument
from .documents.producer import ProducerDocument
from django.utils.text import slugify
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from .forms import TerroirForm,WineRegisterForm,VarietalBlendForm, ProducerForm, WineMarketForm
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.apps import apps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from rest_framework import filters

sidebar_inventory=[
    {'id':'producer','name':'Producers'},
    {'id':'terroir','name':'Wine Regions'},
    {'id':'wine','name':'Wines'},
    {'id':'varietalblend','name':'Varietal'}
]

@login_required
def inventory(request,section):
    #print(f"->{section}")
    Model = apps.get_model('wine', section)
    #print(f"Model {Model}")
    inventory_object = Model.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(inventory_object, 11)

    try:
        inventory_object = paginator.page(page)
    except PageNotAnInteger:
        inventory_object = paginator.page(1)
    except EmptyPage:
        inventory_object = paginator.page(paginator.num_pages)

    return render(request, f'wine/{section}/list.html', 
        {   'section' : section,
            'inventory_object': inventory_object,
            'columns' : [field.name for field in Model._meta.fields if field.name != 'id'],
            'inventory' : [{'name' : [s['name'] for s in sidebar_inventory if s.get('id') == section][0],
                    'count':  Model.objects.count(),
                    'section': section,
                    'search' : 'ON'
                    }]
        })

class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        vinomio_data = [{
                    'name' : [s['name'] for s in sidebar_inventory if s.get('id') == 'producer'][0],
                    'count':  Producer.objects.count(),
                    'section': 'producer',
                },
                {   
                    'name' : [s['name'] for s in sidebar_inventory if s.get('id') == 'terroir'][0],
                    'count':  Terroir.objects.count(),
                    'section': 'terroir',
                },
                {
                    'name' :  [s['name'] for s in sidebar_inventory if s.get('id') == 'wine'][0],
                    'count' : Wine.objects.count(),
                    'section': 'wine',
                },
                {
                    'name' : [s['name'] for s in sidebar_inventory if s.get('id') == 'varietalblend'][0],
                    'count' : VarietalBlend.objects.count(),
                    'section' : 'varietalblend',
                }
        ]
       
        return render(request,'wine/dashboard.html',{'section': 'wine-dashboard','inventory' : vinomio_data})

class WineMarketView(SuccessMessageMixin, CreateView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        wine = Wine.objects.get(pk=kwargs['wineid'])
        form = WineMarketForm(initial={'name':wine, 'terroirname':wine.terroir, 'varietalname':wine.varietal})
        return render(request,'wine/vintage/create.html', {'form': form,})   

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        wine = Wine.objects.get(pk=kwargs['wineid'])
        form = WineMarketForm(request.POST, initial={'name':wine, 'terroirname':wine.terroir, 'varietalname':wine.varietal})
        if form.is_valid():
            form.save(wine=wine)
            messages.success(request, f"blah was created successfully")
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
        return render(request,'wine/vintage/create.html', {'form': form,})        

class WineRegisterView(SuccessMessageMixin, CreateView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        wine_form = WineRegisterForm()
        wine_form.fields['winetype'].choices =Wine.WINETYPE
        #wine_form.fields['winetype'].choices
        return render(request,'wine/register.html', {'wine_form': wine_form,})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        wine_form = WineRegisterForm(request.POST)
        wine_form.fields['winetype'].choices =Wine.WINETYPE
        if wine_form.is_valid():
            wine_form.save()
            messages.success(request, f"blah was created successfully")
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
        else:
            return render(request,'wine/register.html', {'wine_form': wine_form,})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class VarietalBlendUpdateView(SuccessMessageMixin, UpdateView):
    model = VarietalBlend
    fields = ('mastervarietal','varietal')
    template_name = 'wine/varietalblend/detail.html'
    success_url ="/"

class ProducerCreateView(SuccessMessageMixin, CreateView):

    def get(self, request, *args, **kwargs):
        context = {'form': ProducerForm()}
        return render(request, 'wine/producer/create.html', context)
    def post(self, request, *args, **kwargs):
        form = ProducerForm(request.POST)
        if form.is_valid():
            producer = form.save(commit=False)
            producer.save()            
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/varietalblend/create.html', {'form': form})

class VarietalBlendCreateView(SuccessMessageMixin, CreateView):
    #template_name = 'wine/varietalblend/create.html'
    #form_class = VarietalBlendForm
    #success_message = "%(name)s was created successfully"

    #def __str__(self):
    #    return self.title

    #def get_absolute_url(self):
    #    return reverse('books:detail', args=[self.id])
    def get(self, request, *args, **kwargs):
        context = {'form': VarietalBlendForm()}
        return render(request, 'wine/varietalblend/create.html', context)
    
    def post(self, request, *args, **kwargs):
        valueid = request.POST.get('varietalId', None)
        form = VarietalBlendForm(request.POST)
        if form.is_valid():
            form.save()            
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/varietalblend/create.html', {'form': form})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class TerroriCreateView(SuccessMessageMixin, CreateView):
    template_name = 'wine/terroir/create.html'
    form_class = TerroirForm
    success_message = "%(name)s was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

def terrori_detail(request, **kwargs):
    #print("???")
    #print(json.loads(request.body))
    
    data = Terroir.objects.get(pk=json.loads(request.body)['id'])
    subterroirs = Terroir.objects.filter(parentterroir__id=json.loads(request.body)['id'], isvineyard=True)
    serializer = TerroirSerializer(instance=data)
    if request.method == 'POST':
         form = TerroirForm(serializer.data)
    else:
        if request.method == 'DELETE':
            print(f"delete: {json.loads(request.body)}")
        form = TerroirForm(serializer.data)
    return render(request, 'wine/region/detail.html', 
        {  'form': form , 
           'parentterroirid' : dict(serializer.data)['parentterroir'],
           'childterroirs' : subterroirs,
           'terroirid' : dict(serializer.data)['id'],
           #'traverse' : dict(serializer.data)['traverse'] if "traverse" in dict(serializer.data) is not None else None
        })
'''
class VinoMioDocumentViewSet(DocumentViewSet):
    document = VinoMioDocument
    serializer_class = VinoMioDocumentSerializer
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        SimpleQueryStringSearchFilterBackend,
    ]
    search_fields = (
        #'id',
        'producername',
    )
    filter_fields = {
        'id': None,
        'producername' : 'producername', 
    }
    simple_query_string_search_fields = {
        'producername': {'boost': 4},
    }
    ordering_fields = {
        'producername': 'producername',
    }
'''
class ProducerDocumentViewSet(DocumentViewSet):
    document = ProducerDocument
    serializer_class = ProducerDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        #FacetedSearchFilterBackend,
        #FilteringFilterBackend,
        #OrderingFilterBackend,
        #SearchFilterBackend,
        #GeoSpatialFilteringFilterBackend,
        #GeoSpatialOrderingFilterBackend,
        #NestedFilteringFilterBackend,
        DefaultOrderingFilterBackend,
        SuggesterFilterBackend,
        #IdsFilterBackend,
        CompoundSearchFilterBackend,
        SimpleQueryStringSearchFilterBackend,
    ]
    search_fields = (
        #'id',
        'producer',
        'wine',
        'vintage',
    )
    #search_nested_fields = {
    #    'wine': {
    #        'path': 'wine',
    #        'fields': ['name'],
    #    }
    #}
    
    filter_fields = {
        'id': None,
        'vintage' : 'vintage',
    }
    post_filter_fields = {
        'wine_pf': 'wine.name.raw',
        'country_pf': 'city.country.name.raw',
    }
    simple_query_string_search_fields = {
        'producer': {'boost': 4},
        'wine' :  {'boost': 2},
        'vintage' :  {'boost': 1},
    }
    '''
    suggester_fields = {
        'wine_suggest': {
            'field': 'wine.name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }
    
    # Facets
    faceted_search_fields = {
        'wine': {
            'field': 'wine.name.raw',
            'enabled': True,
        },
    }
    ordering_fields = {
        'producername': 'producername',
    }'''
class WineDocumentViewSet(DocumentViewSet):

    document = WineDocument
    serializer_class = WineDocumentSerializer
    lookup_field = 'winename'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        SimpleQueryStringSearchFilterBackend,
    ]
    # Define search fields
    search_fields = (
        #'id',
        'winename',
        'terroir',
        'vintages',
    )
    # Filter fields
    filter_fields = {
        'id': None,
        'winename' : 'winename',
        'vintages' : 'vintages'
        
    }

    simple_query_string_search_fields = {
        'winename': {'boost': 4},
        'terroir': {'boost': 2},
        'vintages': None,
    }

    # Define ordering fields
    ordering_fields = {
        'winename': 'winename',
    }

    # Specify default ordering
    #ordering = ('winename',)   

class VarietalViewSet(viewsets.ModelViewSet):
    queryset = Varietal.objects.all()
    serializer_class = VarietalSerializer
    lookup_field = 'slug'
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = ('slug')

class TerroirListViewSet(ListView):
    template_name = 'wine/terroir/terroir_list.html'
    #context_object_name = 'inventory_object'
    paginate_by = 1000
    
    def get_queryset(self):
        self.terroir = Terroir.objects.filter(parentterroir=self.kwargs['pk']) 
        return self.terroir

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['inventory_object'] = self.terroir
        print(self.kwargs['pk'])
        context['terroir'] = Terroir.objects.get(id=self.kwargs['pk']) 
        return context

class TerroirViewSet(viewsets.ModelViewSet):
    queryset = Terroir.objects.order_by('slug')
    filter_backends = [filters.SearchFilter]
    serializer_class = TerroirSerializer
    search_fields = ['name','parentterroir__name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
    #    print("???")
        queryset = Terroir.objects.all()
        country = self.request.query_params.get('country', None)
        name = self.request.query_params.get('name', None)
        parentterroir = self.request.query_params.get('parentterroir', None)
        recursive = self.request.query_params.get('recursive', None)
        if country is not None:
            queryset = queryset.filter(country__slug=slugify(country))
        if name is not None:
            queryset = queryset.filter(slug=slugify(name))
        if parentterroir is not None:
            queryset = queryset.filter(parentterroir__id=parentterroir)
        return queryset

class MasterVarietalViewSet(viewsets.ModelViewSet):
    #"""API endpoint that allows producers to be viewed or edited."""
     queryset = MasterVarietal.objects.order_by('name')
     serializer_class = MasterVarietalSerializer
     lookup_field = 'slug'
     search_fields = ['name']
     filter_backends = (filters.SearchFilter,)

class VarietalBlendViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = VarietalBlend.objects.all()
    serializer_class = VarietalBlendSerializer
    search_fields = ['mastervarietal']
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = VarietalBlend.objects.all()
        varietal = self.request.query_params.get('items', None)
        if varietal is not None:
            queryset = queryset.filter(varietal__in=[eval(varietal)])
        return queryset

class ProducerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Producer.objects.order_by('-name')
    serializer_class = ProducerSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name']

class WineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Wine.objects.order_by('-name')
    serializer_class = WineSerializer
    lookup_field = 'id'

class CriticViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Critic.objects.order_by('-name')
    serializer_class = CriticSerializer

class MarketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Market.objects.order_by('-wine')
    serializer_class = MarketSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Review.objects.order_by('-score')
    serializer_class = ReviewSerializer

class WineReviewViewSet(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = WineReviewSerializer


class WineRegions2ListView(ListView):
    template_name = 'wine/region/region_list.html'
    context_object_name = 'regions'
    paginate_by = 1000
    queryset = Terroir.objects.all()
    

    def get_subregions(self, parentid, path):
        childregions = Terroir.objects.filter(parentterroir__id=parentid, isvineyard=False)
        if childregions.count() > 0:
           self.__terroirs.append({'id':parentid, 'region': path})
           for region in childregions:
                self.get_subregions(region.id, f'{path}>{region.name}')
        else:
            self.__terroirs.append({'id':parentid, 'region': path})

    def get_queryset(self):
        self.__terroirs = []
        if "regionid" in self.kwargs:
            terroirs =  Terroir.objects.filter(parentterroir__id=self.kwargs['regionid'], isvineyard=False)
            for region in terroirs:
                self.get_subregions(region.id, region.name)
            regionids = [ r['id'] for r in self.__terroirs ]
            print(regionids)
            return Terroir.objects.filter(id__in=regionids)

        return None

class WineRegionsListView(ListView):
    template_name = 'wine/region/list.html'
    queryset = Terroir.objects.all()
    #context_object_name ='regions'

    def get_queryset(self):
        if "regionid" in self.kwargs:
            self.regions = Terroir.objects.filter(parentterroir__id=self.kwargs['regionid'], isvineyard=False)
            return self.regions
        return Terroir.objects.all()
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "regionid" in self.kwargs:
            context['regions'] = self.regions
            context['form'] = TerroirForm()
            context['form_init'] = 'true'
        else:
            country_names = [c['slug'] for c in Country.objects.values('slug')]
            # Add in a QuerySet of all the books
            context['regions'] = Terroir.objects.filter(slug__in=country_names, parentterroir__id__isnull=True)
            context['form'] = TerroirForm()
            context['form_init'] = 'true'
        return context


# Create your views here.
def wine_detail(request, producer, year ,winename):
    wine = get_object_or_404(Market, producerslug=producer,
                                     year=year,
                                     wineslug = winename)
    if wine.observations:
        review = Review.objects.filter(marketitem_id=wine.id)

    return render(request,
                  'wine/producer/detail.html',
                  {'wine': wine, 'review' : review})
    #return HttpResponse("return this string")