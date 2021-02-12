from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView

from wine.views.viewhelper import getInventory
from os.path import basename,splitext

from wine.models import Wine
from wine.forms import WineRegisterForm

section = splitext(basename(__file__))[0]

class WineListView(ListView):
    model = Wine
    paginate_by = 25
    context_object_name = 'wines'
    template_name = 'wine/wine/list.html'
    ordering = ['-name',]

    def get_queryset(self):
        if self.request.GET.get('name', None):
            return Wine.objects.filter(name__icontains=self.request.GET['name'])
        if self.request.GET.get('producer', None):
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
