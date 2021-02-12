import django_filters
from wine.models import Region, Terroir
from django.views.generic.list import ListView

class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        # Get the queryset however you usually would.  For example:
        queryset = super().get_queryset()
        # Then use the query parameters and the queryset to
        # instantiate a filterset and save it as an attribute
        # on the view instance for later.
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        context['filterset'] = self.filterset
        return context

class RegionFilter(django_filters.FilterSet):
    class Meta:
        model = Region
        fields = ['country__slug', ]

        def __init__(self, category, *args, **kwargs):
            super(RegionFilter, self).__init__(*args, **kwargs)
            print("hello")

class TerroirFilter(django_filters.FilterSet):
    class Meta:
        model = Terroir
        fields = ['region__slug', ]