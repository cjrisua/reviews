from django import forms
from .models import Terroir, Wine, VarietalBlend, MasterVarietal,Varietal
from django.utils.translation import gettext_lazy as _
from django.forms.utils import ErrorDict, ErrorList, pretty_name  # NOQA
from django.utils.text import slugify

class VarietalBlendForm(forms.Form):
    name = forms.CharField(label='Master Varietal Name',
                           widget= forms.TextInput(attrs={'placeholder':'Master Varietal...',
                                                          'aria-label': 'Master Varietal...'},
                                                         )) 
    varietal = forms.CharField(label='Varietal Name(s)',
                            widget= forms.TextInput(attrs={'placeholder':'Varietal...',
                                                          'aria-label': 'Varietal...'},
                                                         ))  
    varietalId = forms.CharField(widget= forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.new_mastervarietal = False
        self.mastervarietal = None
        super(VarietalBlendForm, self).__init__(*args, **kwargs)

    def clean_varietalId(self):
        varietal = str(self.cleaned_data['varietalId']).split(',')
        return [id for id in varietal]

    def clean_name(self):
        name = self.cleaned_data['name']
        obj, created = MasterVarietal.objects.get_or_create(slug=slugify(name), defaults={'name':name})
        if created:
            self.new_mastervarietal = True
        self.mastervarietal = obj
        return obj.id

    def save(self):
        mastervarietal = self.cleaned_data['name']
        varietal  = self.cleaned_data['varietalId']
        vblend = VarietalBlend(mastervarietal=MasterVarietal.objects.get(pk=mastervarietal))
        vblend.save()
        for v in varietal:
            vblend.varietal.add(Varietal.objects.get(pk=v))

class TerroirField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
            super(TerroirField, self).__init__(*args, **kwargs)
            #self.error_messages = {"required":"Please select a gender, it's required"}
            #self.choices = ((None,'Select gender'),('M','Male'),('F','Female'))
            self.choices = ((None,'-------'),)
            self.required = False

class TerroirForm(forms.ModelForm):
    #region = TerroirField()
    class Meta:
        model = Terroir
        exclude = ['slug']
        labels = {
            'name' : _('Terroir Name'),
            'parentterroir' : _('Regions'),
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