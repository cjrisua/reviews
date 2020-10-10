from django import forms
from .models import Allocation
from wine.models import Producer
from django.utils.translation import gettext_lazy as _

class AllocationForm(forms.ModelForm):
     class Meta:
        model = Allocation
        fields = '__all__'
        producer = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
        labels = {
            'producer' : _('Producer name'),
            'signupdate' : _('Mailing list sign up date'),
        }
        

class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = ['name']
        labels = {
            'name' : _('Producer Name'),
        }
        