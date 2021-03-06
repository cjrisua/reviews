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

from wine.models import Wine,Market, Review, Vintage, Region
from wine.forms import WineRegisterForm
from functools import reduce

section = splitext(basename(__file__))[0]

class WineDetailListView(ListView):
    model = Market
    context_object_name = 'context'
    template_name = 'wine/wine/detail.html'
    
    def get_queryset(self):
          qs = {
                "market": 
                Market.objects.filter(Q(wine__id=self.kwargs['pk']) | Q(review__isnull=True) & Q(wine__id=self.kwargs['pk'])) \
                    .annotate(user_review=F('review__observation'),
                              user_critic=F('review__critic__name'),
                              user_issuedate=F('review__issuedate'),
                              user_score=F('review__score'),
                              average_rating=Avg('review__score')) \
                    .order_by("-year")
                    }
          averages = [s.user_score for s in qs['market'] if s.user_score]
          qs['score'] = 0 if len(averages) == 0 else reduce(lambda a, b: a + b, averages) / len(averages)
          
          query = '''
             WITH RECURSIVE c AS (
                SELECT id, 
                       region_id,
                       slug
                FROM wine_region
                where id =  %s
                UNION ALL
                SELECT t.id,
                        t.region_id,
                        t.slug
                FROM wine_region as t
                INNER JOIN c on c.region_id = t.id
                )
                SELECT c.id, c.slug from c;
            '''
          parent_regions = Region.objects.raw(query,[qs['market'][0].wine.region.id])

          vintagescores = Vintage.objects.filter(region__region__country__slug=qs['market'][0].wine.region.country.slug, 
                                                 year__in=[y.year for y in qs['market']],
                                                 region__region__id__in=[f.id for f in parent_regions],
                                                 varietal__id=qs['market'][0].wine.varietal_id)
          qs['vintagescore'] = vintagescores
          market_data = {f.year:f.average_rating for f in qs['market']}
          vintage = {f.year:f.score for f in qs['vintagescore']}
          new_data = sorted({**market_data , **vintage}.items(),key=lambda x : {x[0]})
          qs['data'] = {
                        'labels': [f[0]  for f in new_data if f[1]],
                        'datasets': [{
                            'label': "Wine",
                            'type': "line",
                            'borderColor': "#8e5ea2",
                            'data': [0 if not f[0] in market_data else  market_data[f[0]] for f in new_data if f[1]],
                            'fill': 'false'
                            }, 
                            {
                            'label': "Vinate",
                            'type': "line",
                            'borderColor': "#3e95cd",
                            'data': [0 if not f[0] in vintage else  vintage[f[0]] for f in new_data if f[1]],
                            'fill': 'false'
                            },
                            {
                            'label': "Wine",
                            'type': "bar",
                            'backgroundColor': "#3377ff",
                            'data': [0 if not f[0] in market_data else  market_data[f[0]] for f in new_data if f[1]],
                            }, 
                            {
                            'label': "Vinate",
                            'type': "bar",
                            'backgroundColor': "rgba(0,0,0,0.2)",
                            'backgroundColorHover': "#3e95cd",
                            'data': [0 if not f[0] in vintage else  vintage[f[0]] for f in new_data if f[1]],
                            }
                        ]
                        }
          return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class WineListView(ListView):
    model = Wine
    paginate_by = 25
    context_object_name = 'wines'
    template_name = 'wine/wine/list.html'
    ordering = ['-name',]

    def get_queryset(self):
        results = None
        if self.request.GET.get('name', None):
            return Wine.objects.filter(name__icontains=self.request.GET['name'])
        if self.request.GET.get('producer', None):
            if self.request.GET.get('wine', None):
                return Wine.objects.filter(producer__slug=self.request.GET['producer'], slug=self.request.GET['wine'])
            return Wine.objects.filter(producer__slug=self.request.GET['producer'])
        
        return Wine.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory'] = getInventory(section)
        return context
class WineCreateView(SuccessMessageMixin, CreateView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        wine_form = WineRegisterForm()
        #wine_form.fields['winetype'].choices =Wine.WINETYPE
        #wine_form.fields['winetype'].choices
        return render(request,'wine/register.html', {'wine_form': wine_form,})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        wine_form = WineRegisterForm(request.POST)
        #wine_form.fields['winetype'].choices =Wine.WINETYPE
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
