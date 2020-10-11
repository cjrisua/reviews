from django import forms
from .models import Allocation
from wine.models import Producer
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import TextInput

class AllocationForm(forms.ModelForm):
     class Meta:
        model = Allocation
        fields = ('producer','signupdate','status')
        widgets = {
            'producer': TextInput(attrs={'cols': 80, 'rows': 20}),
        }
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
        