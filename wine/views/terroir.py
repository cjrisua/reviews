from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wine.views.viewhelper import getInventory

from django.views.generic.list import ListView
from django.views.generic import UpdateView
from wine.models import Terroir, Country


section = 'terroir'

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
            'region_hidden' : terroir.parentterroir.id,
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
            'country' : country_init,
            'name' : terroir.name,
            'region' : terroir.parentterroir,
            'isappellation': terroir.isappellation,
            'isvineyard' : terroir.isvineyard,
            'choice_initial_id' : (terroir.country.id, terroir.country.name)
        }
        context = {'form': TerroirForm(initial=initial)}
        return render(request, 'wine/terroir/update.html', context)

class TerroirListView(ListView):
    model = Terroir
    paginate_by = 25
    context_object_name = 'regions'
    template_name = 'wine/terroir/list.html'
    ordering = ['-isappellation','-name']

    def get_queryset(self):
        if self.kwargs.get('pk',None) and self.kwargs.get('country',None):
            return Terroir.objects.filter(country__slug=self.kwargs['country'], parentterroir=self.kwargs['pk'])
        elif self.kwargs.get('country',None):
            return Terroir.objects.filter(country__slug=self.kwargs['country'], parentterroir=None)
        elif self.kwargs.get('pk',None):
            return Terroir.objects.filter(parentterroir=self.kwargs['pk'])
        elif self.request.GET.get('name', None):
            return Terroir.objects.filter(name__icontains=self.request.GET['name'])
        return Terroir.objects.filter(parentterroir=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('pk',None):
            context['terroir'] = context['regions'].first().parentterroir
            context['iscountry'] = False
        else:
             context['terroir'] = {'name':context['regions'].first().country.name,
                                   'slug':context['regions'].first().country.slug,
                                   'id': 0,
                                   'parentterroir':0}
             context['iscountry'] = True
        context['inventory'] = getInventory(section)
        return context