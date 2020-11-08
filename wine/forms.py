from django import forms
from .models import Terroir, Wine
from django.utils.translation import gettext_lazy as _
from django.forms.utils import ErrorDict, ErrorList, pretty_name  # NOQA

class TerroirField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
            super(TerroirField, self).__init__(*args, **kwargs)
            #self.error_messages = {"required":"Please select a gender, it's required"}
            #self.choices = ((None,'Select gender'),('M','Male'),('F','Female'))
            self.choices = ((None,'-------'),)
            self.required = False

class TerroirForm(forms.ModelForm):
    region = TerroirField()
    class Meta:
        model = Terroir
        exclude = ['parentterroir','slug']
        labels = {
            'name' : _('Terroir Name'),
            'isappellation' : _('Appelation?'),
            'isvineyard' : _('Vineyard?')
        }

class WineRegisterForm(forms.ModelForm):
    class Meta:
        model = Wine
        fields = ('producer','terroir','varietal','name','wtype',)
        labels = {
            'wtype' : _('Wine Type'),
            'isappellation' : _('Appelation?'),
            'isvineyard' : _('Vineyard?')
        }