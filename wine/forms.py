from django import forms
from .models import Terroir, Wine, VarietalBlend, MasterVarietal,Varietal,Producer
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

#class WineRegisterForm(forms.ModelForm):
#    class Meta:
#        model = Wine
#        fields = ('producer','terroir','varietal','name','wtype',)
#        labels = {
#            'wtype' : _('Wine Type'),
#            'isappellation' : _('Appelation?'),
#            'isvineyard' : _('Vineyard?')
#        }
class WineRegisterForm(forms.Form):

    producername = forms.CharField(label='Producer Name',
                           widget= forms.TextInput(attrs={'placeholder':'Producer name',
                                                          'aria-label': 'Producer name'},
                                                         )) 
    terroirname = forms.CharField(label='Terroir Name',
                           widget= forms.TextInput(attrs={'placeholder':'Terroir name',
                                                          'aria-label': 'Terroir name'},
                                                         )) 
    varietalname = forms.CharField(label='Primary Varietal Name',
                           widget= forms.TextInput(attrs={'placeholder':'Varietal name',
                                                          'aria-label': 'Varietal name'},
                                                         ))  
    name = forms.CharField(label='Wine Name',
                           widget= forms.TextInput(attrs={'placeholder':'Varietal name',
                                                          'aria-label': 'Varietal name'},
                                                         ))         
    winetype = forms.ChoiceField(label='Wine Style')

    ''' Hidden Fileds '''
    producer = forms.CharField(widget=forms.HiddenInput)
    terroir = forms.CharField(widget=forms.HiddenInput)
    varietal = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(WineRegisterForm, self).__init__(*args, **kwargs)

    def save(self):
        producer = Producer.objects.get(pk=self.cleaned_data['producer'])
        terroir = Terroir.objects.get(pk=self.cleaned_data['terroir'])
        varietal = VarietalBlend.objects.get(mastervarietal__id=self.cleaned_data['varietal'])
        wine = Wine(producer=producer,
                    terroir=terroir,
                    varietal=varietal,
                    name=self.cleaned_data['name'],
                    wtype =self.cleaned_data['winetype'])
        wine.save()

        
class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = ('name',)