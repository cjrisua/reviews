from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView
from django.db.models import Q, F, Avg
from wine.views.viewhelper import getInventory
from os.path import basename,splitext
from django.http import HttpResponse, JsonResponse
from wine.models import Vintage, VintageRegion
from wine.forms import VintageForm, VintageRegionForm
from wine.serializers import VintageChartSerializer
from functools import reduce
from itertools import groupby
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

section = splitext(basename(__file__))[0]

class Base(ListView):
    context_object_name = 'context'
    
    def get_queryset(self):
          #market = Market.objects.get(id=self.kwargs['pk'])
          #reviews = Review.objects.filter(marketitem__id=self.kwargs['pk'])
          return self.model.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory'] = getInventory(section if not self.section else self.section)
        return context
    def __init__(self, **kwargs):
        self.section = kwargs.get('section',None)
        super().__init__()

class VintageListView(Base):
    model = Vintage
    template_name = 'wine/vintage/list.html'
    #ordering = ['-region__region__country','-year','-region__region',]
    ordering = ['-region__region',]

    def __init__(self):
        super().__init__(section=['vintageregion','vintage'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #content['vintage_chart'] = context['context'].objects.distinct('region__region__country')
        serializer = VintageChartSerializer(Vintage.objects.all(),many=True)
        context['serializer'] = sorted(serializer.data, key=lambda x: (x['country_name'],x['region_name']), reverse=False)
        return context

class VintageRegionListView(Base):
    model = VintageRegion
    template_name = 'wine/vintage/region/list.html'
    ordering = ['-name']

    def __init__(self):
        super().__init__(section='vintageregion')

class VintageRegionCreateView(SuccessMessageMixin, CreateView):

    def dispatch(self, *args, **kwargs):
        self.__initial = {}
        self.__context = {}
        self.__context['inventory'] = getInventory('vintageregion')[0]
        return super().dispatch(*args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.__context['form'] = VintageRegionForm(initial=self.__initial)
        return render(request, 'wine/vintage/region/create.html', self.__context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = {'form': VintageRegionForm(request.POST, initial=self.__initial)}
        if context['form'].is_valid():
            context['form'].save()
            params={}
            #if context['form'].result:
            #    params = {'country': context['form'].result.country.slug}
            #    if context['form'].result.region is not None:
            #        params['region']=context['form'].result.region.slug
            return HttpResponseRedirect(reverse_lazy('wine:vintageregion_list', kwargs=params))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/vintage/region/create.html', context)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class VintageCreateView(SuccessMessageMixin, CreateView):

    def dispatch(self, *args, **kwargs):
        self.__initial = {}
        return super().dispatch(*args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': VintageForm(initial=self.__initial)}
        return render(request, 'wine/vintage/create.html', context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = {'form': VintageForm(request.POST, initial=self.__initial)}
        if context['form'].is_valid():
            context['form'].save()
            params={}
            #if context['form'].result:
            #    params = {'country': context['form'].result.country.slug}
            #    if context['form'].result.region is not None:
            #        params['region']=context['form'].result.region.slug
            return HttpResponseRedirect(reverse_lazy('wine:vintage_list', kwargs=params))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/vintage/create.html', context)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
