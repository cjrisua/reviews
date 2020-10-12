from django import forms
from .models import Allocation
from wine.models import Producer
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import TextInput, HiddenInput
from django.forms.fields import DateField

class AllocationModelForm(forms.ModelForm):
     class Meta:
        model = Allocation
        fields = ('producer','signupdate','status','addeddate','mailingmonths','lastpurchasedate','inactivitypenalty',)
        widgets = {
            'producer' : HiddenInput(),
        }
        labels = {
            'signupdate' : _('Mailing list sign up date'),
        }
class AllocationForm(AllocationModelForm, forms.Form):        
        producer_name = forms.CharField(widget=TextInput(attrs={'cols': 80, 'rows': 20}))

class AllocationUpdateForm(AllocationModelForm, forms.Form):  
        def __init__(self, instance, *args, **kwargs):
            super(AllocationUpdateForm, self).__init__(instance=instance)
            self.producer_name = instance
            self.post = kwargs
        
        def is_valid(self):
            return True

        def form_valid(self, form, *args, **kwargs):
            print("form_valid")
            
        def save(self, commit=True, *args, **kwargs):
            allocation = super(AllocationUpdateForm, self).save(commit=False)
            updated, created = Allocation.objects.update_or_create(
                producer=self.instance.producer,
                defaults={'addeddate': self.post['data']['addeddate']},
                )
            return updated

        
class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = ['name']
        labels = {
            'name' : _('Producer Name'),
        }
        