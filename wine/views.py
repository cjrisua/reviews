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
                            MasterVarietalSerializer, VarietalBlendSerializer)
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .documents import WineDocument
from django.utils.text import slugify
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views import View
from .forms import TerroirForm,WineRegisterForm,VarietalBlendForm
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


@login_required
def inventory(request,section):

    Model = apps.get_model('wine', section)
    print(f"Model {Model}")
    inventory_object = Model.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(inventory_object, 20)

    try:
        inventory_object = paginator.page(page)
    except PageNotAnInteger:
        inventory_object = paginator.page(1)
    except EmptyPage:
        inventory_object = paginator.page(paginator.num_pages)

    #print(inventory_object)
    #print([field for field in Model._meta.fields])
    return render(request, f'wine/{section}/list.html', 
        {   'section' : section,
            'inventory_object': inventory_object,
            'columns' : [field.name for field in Model._meta.fields if field.name != 'id']
        })

class Dashboard(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        vinomio_data = [{
                    'name' : 'Producers',
                    'count':  Producer.objects.count(),
                    'section': 'producer',
                },
                {   
                    'name' : 'Wine Regions',
                    'count':  Terroir.objects.count(),
                    'section': 'terroir',
                },
                {
                    'name' :  'Wines',
                    'count' : Wine.objects.count(),
                    'section': 'wine',
                },
                {
                    'name' : 'Varietal',
                    'count' : VarietalBlend.objects.count(),
                    'section' : 'varietalblend',
                }
        ]
       
        return render(request,
                  'wine/dashboard.html',
                  {
                   'section': 'wine-dashboard',
                   'inventory' : vinomio_data
                  })

@login_required
def register(request):
    if request.method == 'POST':
        wine_form = WineRegisterForm(request.POST)
        if wine_form.is_valid():
            new_wine = wine_form.save(commit=False)
            new_wine.save()
            messages.success(request, f"{new_wine.name} was created successfully")
            print(reverse_lazy('wine:wine_dashboard'))
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
            #return render(request,
            #              'wine/dashboard.html',
            #              {})
    else:
        wine_form = WineRegisterForm()
    
    return render(request,
                  'wine/register.html',
                  {'wine_form': wine_form,

                  })
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
        request.POST.get('office_id', None)
        form = VarietalBlendForm(request.POST)
        if form.is_valid():
            book = form.save()
            book.save()
            return HttpResponseRedirect(reverse_lazy('books:detail', args=[book.id]))
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

class WineDocumentViewSet(DocumentViewSet):

    document = WineDocument
    serializer_class = WineDocumentSerializer

    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]
    # Define search fields
    search_fields = (
        'name',
        #'review',
    )
    # Filter fields
    filter_fields = {
        'id': {
            'field': 'id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'name': 'name.raw',
        #'review': 'review.raw',
        'producer': {
            'field': 'producer_id',
            'lookups': [
                LOOKUP_QUERY_IN,
            ]
        },
    }
    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'name': 'name.raw',
        'producer': 'producer_id',
    }

    # Specify default ordering
    ordering = ('id',)   

class VarietalViewSet(viewsets.ModelViewSet):
    queryset = Varietal.objects.all()
    serializer_class = VarietalSerializer
    lookup_field = 'slug'
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = ('abbreviation')

class TerroirViewSet(viewsets.ModelViewSet):
    queryset = Terroir.objects.order_by('slug')
    serializer_class = TerroirSerializer
    #lookup_field = 'slug'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        #print("???")
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
    """
    API endpoint that allows producers to be viewed or edited.
    """
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