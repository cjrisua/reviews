
from django.views.generic.list import ListView
from wine.views.viewhelper import getInventory
from os.path import basename,splitext
from wine.models import Market, Review

section = splitext(basename(__file__))[0]

class MarketDetailListView(ListView):
    model = Market
    context_object_name = 'context'
    template_name = 'wine/market/detail.html'

    def get_queryset(self):
          market = Market.objects.get(id=self.kwargs['pk'])
          reviews = Review.objects.filter(marketitem__id=self.kwargs['pk'])
          return {'market' : market, 'reviews': reviews}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context