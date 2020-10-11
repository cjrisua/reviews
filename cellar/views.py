from django.shortcuts import render
from .models import Collection, Allocation
from .serializers import CollectionSerializer
from rest_framework import viewsets
from django.views import View
from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView
from .forms import AllocationForm, ProducerForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

class ProducerCreateView(CreateView):
    #template_name = 'allocation/producer-create.html'
    #form_class = ProducerForm

    def post(self, request, *args, **kwargs):
       form = ProducerForm(request.POST)
       if form.is_valid():
           producer = form.save()
           producer.save()
           return HttpResponseRedirect(reverse_lazy('cellar:allocation_create'))
       else:
            print("Invalid", form.errors)
       return render(request, 'allocation/create.html', {'form': AllocationForm()})

class AllocationUpdateView(UpdateView):
    model = Allocation
    template_name = 'allocation/detail.html'
    #fields = '__all__'
    form_class = AllocationForm
    
class AllocationCreateView(CreateView):
     #template_name = 'allocation/detail.html'
     #form_class = AllocationForm

     def get(self, request, *args, **kwargs):
        context = {'form': AllocationForm(),
                   'producerform': ProducerForm() 
                  }
        return render(request, 'allocation/create.html', context)

     def post(self, request, *args, **kwargs):
        print(request.POST)
        #request.POST['producer'] = request.POST['producer_id'] 
        new_request = request.POST.copy()
        #new_request['producer'] =  request.POST['producer_id'] 
        form = AllocationForm(new_request)
        if form.is_valid():
            allocation = form.save()
            allocation.save()
            return HttpResponseRedirect(reverse_lazy('cellar:allocation'))
        else:
             print("Invalid", form.errors)
        return render(request, 'allocation/create.html', {'form': form,'producerform': ProducerForm() })

class AllocationListView(ListView):
    template_name = 'allocation/list.html'
    queryset = Allocation.objects.order_by('status')
    context_object_name ='allocations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CollectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows producers to be viewed or edited.
    """
    queryset = Collection.objects.order_by('-collectible')
    serializer_class = CollectionSerializer

class CollectionListView(ListView):
    #module = Collection
    template_name = 'cellar/collection/list.html'
    queryset = Collection.objects.all()
    context_object_name ='collection'