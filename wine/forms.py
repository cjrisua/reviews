from django import forms
from .models import Market, Terroir, Wine, VarietalBlend, MasterVarietal,Varietal,Producer, Country
from django.utils.translation import gettext_lazy as _
from django.forms.utils import ErrorDict, ErrorList, pretty_name  # NOQA
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import django.shortcuts 
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

class BaseChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
            super(BaseChoiceField, self).__init__(*args, **kwargs)
            self.choices = [(None,'-------'),]
            self.required = False

class TerroirForm(forms.Form):
    country = BaseChoiceField(label='Country Name',required=True)
    region_hidden = forms.CharField(widget=forms.HiddenInput(), required=False)

    region = forms.CharField(label='Region Name',
                           widget= forms.TextInput(attrs={'placeholder':'Region name',
                                                          'aria-label': 'Region name'}
                                                         ),required=False)
    name = forms.CharField(label='Terroir Name',
                           widget= forms.TextInput(attrs={'placeholder':'Terroir name',
                                                          'aria-label': 'Terroir name'}
                                                         ),required=True)
    isappellation = forms.BooleanField(label='Is an Appellation', required=False)
    isvineyard = forms.BooleanField(label='Is a Vineyard', required=False)

    def __init__(self, *args, **kwargs):
        super(TerroirForm, self).__init__(*args, **kwargs)
        choice_init = self.fields['country'].choices
        if self.initial.get('country',None):
            choice_init.extend([(x[0],x[1]) for x in self.initial['country']])
        self.fields['country'].choices = choice_init
        if self.initial.get('choice_initial_id',None):
            self.fields['country'].choices.pop(0)
            index = self.fields['country'].choices.index(self.initial['choice_initial_id'])
            self.fields['country'].choices = self.fields['country'].choices[index:] + self.fields['country'].choices[:index]
    def clean_country(self):
        return Country.objects.get(pk=self.cleaned_data['country'])
    def clean_region_hidden(self):
        if self.cleaned_data['region_hidden'] == '':
         return self.initial.get('region_hidden')
        return self.cleaned_data['region_hidden']
    def clean_region(self):
        if self.cleaned_data['region'] == '':
            return None
        else:
            terroir = Terroir.objects.get(pk=self.cleaned_data['region_hidden'])
            if terroir:
                return terroir
            else:
                 raise ValidationError("Region not found!")
    def clean_name(self):
        data = self.cleaned_data['name']
        country = None
        if self.cleaned_data.get('country',None):
            country = self.cleaned_data['country']
        else:
            country = Country.objects.get(pk=self.data['country'])

        exists = Terroir.objects.filter(
                        slug=slugify(self.cleaned_data['name']), 
                        country=country,
                        parentterroir=self.cleaned_data['region']).exists()
        if exists and self.cleaned_data['region'] != self.initial['region']:
            raise ValidationError(f"Terroir {data} already exists")
        return data
    def save(self,**kwargs):
        obj, created = Terroir.objects.update_or_create(
            id=self.initial.get('id',None),
            defaults={
                        'country': self.cleaned_data['country'],
                        'parentterroir':self.cleaned_data['region'],
                        'name':self.cleaned_data['name'],
                        'isappellation':self.cleaned_data['isappellation'],
                        'isvineyard':self.cleaned_data['isvineyard']
                    }
        )
    #class Meta:
    #    model = Terroir
    #    exclude = ['slug']
    #    labels = {
    #        'name' : _('Terroir Name'),
    #        'parentterroir' : _('Regions'),
    #        'isappellation' : _('Appelation?'),
    #        'isvineyard' : _('Vineyard?')
    #   }
class WineMarketForm(forms.Form):

    vintage = forms.CharField(label='Vintage',
                           widget= forms.TextInput(attrs={'placeholder':'Vintage',
                                                          'aria-label': 'Vintage'},
                                                         ))

    name = forms.CharField(label='Wine Name',
                           widget= forms.TextInput(attrs={'placeholder':'Varietal name',
                                                          'aria-label': 'Varietal name',}
                                                         ),required=False) 
    terroirname = forms.CharField(label='Terroir Name',
                           widget= forms.TextInput(attrs={'placeholder':'Terroir name',
                                                          'aria-label': 'Terroir name'}
                                                         ),required=False)
    varietalname = forms.CharField(label='Primary Varietal Name',
                           widget= forms.TextInput(attrs={'placeholder':'Varietal name',
                                                          'aria-label': 'Varietal name'}
                                                         ),required=False)                                               

    price = forms.CharField(label='Release Price',
                           widget= forms.TextInput(attrs={'placeholder':'Price $$$',
                                                          'aria-label': 'Price $$$'},
                                                         ))
    def __init__(self, *args, **kwargs):
        super(WineMarketForm, self).__init__(*args, **kwargs)
        self.fields['name'].disabled = True
        self.fields['terroirname'].disabled = True
        self.fields['varietalname'].disabled = True

    def save(self,**kwargs):
        market = Market(wine=kwargs['wine'],
                        varietal=kwargs['wine'].varietal,
                        producerslug=kwargs['wine'].producer.slug,
                        wineslug=slugify(kwargs['wine']),
                        price=self.cleaned_data['price'],
                        year=self.cleaned_data['vintage'])
        market.save()
        
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