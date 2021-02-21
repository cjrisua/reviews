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
from wine.views.viewhelper import getInventory
from wine.models import Producer
from os.path import basename,splitext
from django.views.generic.edit import CreateView
from wine.forms import ProducerForm

section = splitext(basename(__file__))[0]

class ProducerListView(ListView):
    model = Producer
    paginate_by = 25
    context_object_name = 'producers'
    template_name = 'wine/producer/list.html'
    ordering = ['-name',]

    def get_queryset(self):
        if self.request.GET.get('name', None):
            return Producer.objects.filter(name__icontains=self.request.GET['name'])
        else:
            return Producer.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory'] = getInventory(section)
        return context

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
