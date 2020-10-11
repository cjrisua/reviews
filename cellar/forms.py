from django import forms
from .models import Allocation
from wine.models import Producer
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import TextInput, HiddenInput

class AllocationModelForm(forms.ModelForm):
     class Meta:
        model = Allocation
        fields = ('producer','signupdate','status','addeddate','mailingmonths','inactivitypenalty','lastpurchasedate')
        widgets = {
            'producer' : HiddenInput(),
        }
        labels = {
            'signupdate' : _('Mailing list sign up date'),
        }
class AllocationForm(AllocationModelForm, forms.Form):        
        producer_name = forms.CharField(widget=TextInput(attrs={'cols': 80, 'rows': 20}))
        
class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = ['name']
        labels = {
            'name' : _('Producer Name'),
        }
        