from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from wine.views.viewhelper import getInventory
from wine.views.filters import FilteredListView,TerroirFilter

from wine.forms import TerroirForm
from wine.models import Terroir, Country, Region

from django.views.generic.list import ListView
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView

section = 'terroir'

class TerroriCreateView(SuccessMessageMixin, CreateView):
    #template_name = 'wine/terroir/create.html'
    #form_class = TerroirForm
    success_message = "%(name)s was created successfully"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        
        country_init = Terroir.objects.order_by().values_list('country__id','country__name').distinct()
        
        context = {'form': TerroirForm(request.POST, initial={'country':country_init})}
        if context['form'].is_valid():
            context['form'].save()
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/terroir/create.html', context)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        country_init = Terroir.objects.order_by().values_list('country__id','country__name').distinct()
        context = {'form': TerroirForm(initial={'country':country_init})}
        return render(request, 'wine/terroir/create.html', context)


class TerroirUpdateView(SuccessMessageMixin, UpdateView):
    success_message = "%(name)s was updated successfully"
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        country_init = Terroir.objects.order_by().values_list('country__id','country__name').distinct()
        terroir = Terroir.objects.get(pk=self.kwargs['pk'])
        initial={
            'id' : self.kwargs['pk'],
            'country' : country_init,
            'name' : terroir.name,
            'region' : terroir.parentterroir,
            'isappellation': terroir.isappellation,
            'isvineyard' : terroir.isvineyard,
            'region_hidden' : terroir.parentterroir.id if terroir.parentterroir is not None else None,
            'choice_initial_id' : (terroir.country.id, terroir.country.name)
        }
        context = {'form': TerroirForm(request.POST, initial=initial)}
        if context['form'].is_valid():
            context['form'].save()
            return HttpResponseRedirect(reverse_lazy('wine:wine_dashboard'))
        else:
             messages.add_message(request, messages.ERROR, 'Something went wrong!')
        return render(request, 'wine/terroir/update.html', context)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        country_init = Terroir.objects.order_by().values_list('country__id','country__name').distinct()
        terroir = Terroir.objects.get(pk=self.kwargs['pk'])
        initial={
            'id' : self.kwargs['pk'],
            'country' : country_init,
            'name' : terroir.name,
            'region' : terroir.parentterroir,
            'isappellation': terroir.isappellation,
            'isvineyard' : terroir.isvineyard,
            'isunknown' : terroir.isunknown,
            'choice_initial_id' : (terroir.country.id, terroir.country.name)
        }
        context = {'form': TerroirForm(initial=initial)}
        return render(request, 'wine/terroir/update.html', context)

class TerroirListView(ListView):
    model = Region
    paginate_by = 25
    context_object_name = 'regions'
    template_name = 'wine/terroir/list.html'
    ordering = ['-name']
    
    def get_queryset(self):
        qs = None
        '''
        if self.kwargs.get('pk',None) and self.kwargs.get('country',None):
            qs = Terroir.objects.filter(country__slug=self.kwargs['country'], parentterroir=self.kwargs['pk'])
        elif self.kwargs.get('country',None):
            qs = Terroir.objects.filter(country__slug=self.kwargs['country'], parentterroir=None)
        elif self.kwargs.get('pk',None):
            terroir = Terroir.objects.filter(parentterroir=self.kwargs['pk'])
            #if terroir.count() == 0:
            #    return Terroir.objects.filter(id=self.kwargs['pk'])
            qs = terroir
        elif self.request.GET.get('name', None):
            terroir = Terroir.objects.filter(name__icontains=self.request.GET['name'])
            #result = [(t,Terroir.objects.filter(parentterroir=t.id).count()) for t in terroir]
            #result.sort(key = lambda x: -x[1])
            #qs = [r[0] for r in result]
            qs = terroir
        else:  
            qs = Terroir.objects.filter(parentterroir=None)

        if self.request.GET.get('isunknown',None) and self.request.GET['isunknown'] != 'true':
            qs = qs.exclude(isunknown=True)
            
        '''
        return Region.objects.all()
        #result = #TerroirFilter(self.request.GET, queryset=qs)
        #return result.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('pk',None):
            if len(context['regions']) != 0:
                context['terroir'] = context['regions'][0].region
            else:
                context['terroir'] =  Region.objects.get(id=self.kwargs['pk'])

            context['iscountry'] = False
        elif len(context['regions']) > 0:
             context['terroir'] = {'name':context['regions'][0].country.name,
                                   'slug':context['regions'][0].country.slug,
                                   'id': 0,
                                   'parentterroir':0}
             context['iscountry'] = True
        context['inventory'] = getInventory(section)
        return context