from django.db import models
from django.utils.text import slugify
from jsonfield import JSONField
from django.utils.text import slugify
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj


class Varietal(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=150,unique=True)
    class Meta:
        ordering = ('-name',)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Varietal, self).save(*args, **kwargs)

class Country(models.Model):
    name = models.CharField(max_length=150)
    abbreviation = models.CharField(max_length=3, blank=False, null=False, default='',unique=True) 
    productionrank = models.DecimalField(default=0, decimal_places=2,max_digits=5 )
    slug = models.CharField(max_length=150, blank=False, null=False, default='')
    class Meta:
        ordering = ('-productionrank','-name',)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Country, self).save(*args, **kwargs)

class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='countryregion')
    region = models.ForeignKey('self', related_name='parentregion', on_delete=models.CASCADE, default=None, blank=True, null=True)
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=150)

    class Meta:
        unique_together = ['country', 'slug', 'region']
        ordering = ('country','region__id')
    
    @property
    def region_traverse(self): 
        parent_name = f'{self.country.name}' if self.country is not None else self.country
        region_names = Region.traverse_region(self, self.region, f'{parent_name} > {self.name}')
        return self.__traversed_name

    @staticmethod
    def traverse_region(self, region ,name):
        if region is not None and region.region is not None:
            name = Region.traverse_region(self, region.region, f'{region.region.name} > {name}')
        else:
           self.__traversed_name = name
    #@property
    #def with_subterroir(self):
    #    return True if Terroir.objects.filter(parentterroir=self.id).exists() else False
    #
    #@property
    #def region_traverse(self): 
    #    parent_name = f'{self.parentterroir.name}' if self.parentterroir is not None else self.country
    #    region_names = Terroir.traverse_region(self, self.parentterroir, f'{parent_name} > {self.name}')
    #    return self.__traversed_name
    
    @property
    def related_regions(self): 
        hierarchy = []
        Region.traverseregion(self,hierarchy)
        hierarchy.reverse()
        return hierarchy[:-1]

    @staticmethod
    def traverseregion(self,hierarchy):
        hierarchy.append(self)
        if self.region is not None:
            Region.traverseregion(self.region,hierarchy)
            
        
    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Region, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.__traversed_name = None
        self.__hierarchy = []
        super().__init__(*args, **kwargs)

class Terroir(models.Model):
    #country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_region')
    #parentterroir = models.ForeignKey('self', blank='True', null=True, related_name='subterroir', on_delete=models.CASCADE, default=-1)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='regionarea', default=None)
    name = models.CharField(max_length=150)
    isappellation = models.BooleanField(default=False)
    isvineyard = models.BooleanField(default=False)
    slug = models.CharField(max_length=150, blank=False, null=False, default='')
    isunknown = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['region','slug']
        ordering = ('region__region__slug','slug')

    @staticmethod
    def traverse_terroir(self, terroir, name):
        if terroir is not None and terroir.parentterroir is not None:
            name = Terroir.traverse_terroir(self, terroir.parentterroir, f'{terroir.parentterroir.name} > {name}')
        else:
           self.__traversed_name = name
    @property
    def with_subterroir(self):
        return True if Terroir.objects.filter(parentterroir=self.id).exists() else False

    @property
    def region_traverse(self): 
        parent_name = f'{self.parentterroir.name}' if self.parentterroir is not None else self.country
        region_names = Terroir.traverse_terroir(self, self.parentterroir, f'{parent_name} > {self.name}')
        return self.__traversed_name
    @property
    def related_regions(self): 
        hierarchy = []
        Terroir.traverse_region(self,hierarchy)
        hierarchy.reverse()
        return hierarchy[:-1]

    @staticmethod
    def traverse_region(self,hierarchy):
        hierarchy.append(self)
        if self.parentterroir is not None:
            Terroir.traverse_region(self.parentterroir,hierarchy)
            
        
    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Terroir, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.__traversed_name = None
        self.__hierarchy = []
        super().__init__(*args, **kwargs)

class Producer(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(unique=True, max_length=150, blank=False, null=False, default='')

    class Meta:
        ordering = ('name',)
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Producer, self).save(*args, **kwargs)

    @property
    def producer_indexing(self):
        if self.name is not None:
            return f"{self.name}"
    @property
    def winename_indexing(self):
        wrapper = []
        if self.name is not None:
            wine_data = Wine.objects.filter(producer__id=self.id)
            wines = [w for w in wine_data]
            for wine in wines:
                '''return dict_to_obj({
                    'name': wine.name,
                    'vintages': {
                        'vintage': [v.year for v in Market.objects.filter(wine__id=wine.id)]
                    }
                })'''
                wrapper.append(dict_to_obj({
                    'name': wine.name,
                    'vintages': {
                        'vintage': [v.year for v in Market.objects.filter(wine__id=wine.id)]
                    }
                }))
        return wrapper
        '''
        wines_results =[]
        if self.name is not None:
            wine_data = Wine.objects.filter(producer__id=self.id)
            wines = [w for w in wine_data]
            for w in wines:
                years = [v.year for v in Market.objects.filter(wine__id=w.id)]
                for y in years:
                    wines_results.append(f"{w.name}")
            return wines_results
        '''
    '''
    @property
    def vintages_indexing(self):
        wines_results =[]
        if self.name is not None:
            wine_data = Wine.objects.filter(producer__id=self.id)
            wines = [w for w in wine_data]
            for w in wines:
                return [v.year for v in Market.objects.filter(wine__id=w.id)]
        return wines_results
    '''
class MasterVarietal(models.Model):
    SPARKLING_WINE = 'SW'
    LIGHTBODIED_WHITE_WINE = 'LBW'
    FULLBODIED_WHITE_WINE = 'FBW'
    AROMATIC_WHITE_WINE = 'AWW'
    ROSE_WINE = 'RW'
    LIGHTBODIED_RED_WINE = 'LBR'
    MEDIUMBODIED_RED_WINE = 'MBR'
    FULLBODIED_RED_WINE = 'FBR'
    DESSERT_WINE = 'DW'
    NONE = 'NONE'

    WINETYPE = models.TextChoices = (
        (SPARKLING_WINE, 'Sparkling Wine'),
        (LIGHTBODIED_WHITE_WINE, 'Light-Bodied White Wine'),
        (FULLBODIED_WHITE_WINE, 'Full-Bodied White Wine'),
        (AROMATIC_WHITE_WINE,'Aromatic White Wine'),
        (ROSE_WINE,'Rosé Wine'),
        (LIGHTBODIED_RED_WINE,'Light-Bodied Red Wine'),
        (MEDIUMBODIED_RED_WINE,'Medium-Bodied Red Wine'),
        (FULLBODIED_RED_WINE,'Full-Bodied Red Wine'),
        (DESSERT_WINE,'Dessert Wine')
    )

    name = models.CharField(max_length=150, unique=True)
    slug = models.CharField(unique=True, max_length=150, blank=False, null=False, default='')
    type = models.CharField(
        max_length=4,
        choices=WINETYPE,
        default='NONE'
    )

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(MasterVarietal, self).save(*args, **kwargs)

class VarietalBlend(models.Model):
    mastervarietal = models.ForeignKey(MasterVarietal, on_delete=models.PROTECT)
    varietal = models.ManyToManyField(Varietal)

    def __str__(self):
        varietalstr = None
        varietallst = [f.name for f in self.varietal.all()]
        if len(varietallst) > 1:
            varietalstr = str(', '.join(varietallst[:-1])) + " and " + varietallst[-1:][0]
        else:
            varietalstr = varietallst[0]
        return f"{self.mastervarietal.name} ({varietalstr})"
        
class Wine(models.Model):
    
    producer = models.ForeignKey(Producer, related_name='wines', on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=False)
    varietal = models.ForeignKey(VarietalBlend, on_delete=models.PROTECT, blank=False)
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=256, default='')

    class Meta:
        indexes = [models.Index(fields=['slug', 'producer'])]

    def __str__(self):
        return f"{self.producer} {self.name}"
    @property
    def wine_indexing(self):

        """Wine for indexing.
        Used in Elasticsearch indexing.
        """
        print('adding wine_indexing...')
        if self.name is not None:
            return f"{self.producer.name} {self.name}"
    @property
    def region_indexing(self):
        print(f'adding region_indexing...pk {self.id}')
        if self.region is not None:
              return [str(terroirname).strip(" ")  for terroirname in str(self.region.region_traverse).split('>')]

    @property
    def vintages_indexing(self):

        """Wine for indexing.
        Used in Elasticsearch indexing.
        """
        #print(f'adding vintages_indexing...pk {self.id}')
        if self.name is not None:
            return [v.year for v in Market.objects.filter(wine__id=self.id)]
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Wine, self).save(*args, **kwargs)

    class Meta:
        unique_together = ['producer', 'name']
        ordering = ['name']

class Critic(models.Model):
     name = models.CharField(max_length=50)

     def __str__(self):
        return self.name

class Market(models.Model):
    wine =  models.ForeignKey(Wine, related_name='vintage',  on_delete=models.CASCADE, blank=False, default=None)
    varietal = models.ForeignKey(VarietalBlend, on_delete=models.PROTECT)
    observations = models.ManyToManyField(Critic, through='Review')
    producerslug = models.SlugField(max_length=200, null=True)
    wineslug = models.SlugField(max_length=200, null=True)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    year = models.CharField(max_length=4, blank=False)
    

    class Meta:
        unique_together = ['year', 'wine_id']
        ordering = ['wine_id','-year']
    def __str__(self):
        return f"{self.year} {self.wine.producer.name} {self.wine.name}"

    def save(self, *args, **kwargs):
        # just check if name or location.name has changed
        self.producerslug = slugify(self.wine.producer.name)
        self.wineslug = slugify(self.wine.name)
        super(Market, self).save(*args, **kwargs)
    @property
    def wine_indexing(self):
        """Wine for indexing.
        Used in Elasticsearch indexing.
        """
        if self.wine is not None:
            return self.__str__()
    @property
    def varietal_indexing(self):
        """Wine for indexing.
        Used in Elasticsearch indexing.
        """
        if self.varietal is not None:
            return [  {"name":v.name, "pk": v.id} for v in self.varietal.varietal.all()]
    @property
    def reviews_indexing(self):
        """Wine for indexing.
        Used in Elasticsearch indexing.
        """
        if self.observations is not None:
            return self.observations.name

class Review(models.Model):
    critic = models.ForeignKey(Critic, on_delete=models.CASCADE)
    marketitem = models.ForeignKey(Market, on_delete=models.CASCADE, blank=True)
    issuedate = models.DateField(blank=False)
    observation = models.TextField()
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['critic','marketitem']
        ordering = ['score']
    

class InboundException(models.Model):
    indoundid = models.IntegerField(blank=False)
    house = models.CharField(max_length=150)
    terroir = models.CharField(max_length=150)
    metadata = JSONField()

    class Meta:
        unique_together = ['indoundid','id']

    def __str__(self):
        return f"{self.house} {self.terroir}"

class ProducerWine(models.Model):
    id = models.BigIntegerField(primary_key=True)
    producer = models.ForeignKey(Producer, on_delete=models.DO_NOTHING)
    wine = models.ForeignKey(Wine, on_delete=models.DO_NOTHING, blank=True)
    market = models.ForeignKey(Market, on_delete=models.DO_NOTHING, blank=True)

    class Meta:
        managed = False
        db_table = 'wine_searchindexview'
        ordering = ['producer__name','-market__year']

    @property
    def producername_indexing(self):
        print("producername_indexing")
        if self.producer is not None:
            return self.producer.name
        
    @property
    def winename_indexing(self):
        print("winename_indexing")
        if self.wine is not None:
            return self.wine.name
    @property
    def winevintage_indexing(self):
        print("winevintage_indexing")
        if self.market is not None:
             return self.market.year

class VintageRegion(models.Model):
    name = models.CharField(max_length=150)
    region = models.ManyToManyField(Region)
    slug = models.CharField(max_length=150)
    
    class Meta:
        unique_together = ['slug']

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # just check if name or location.name has changed
        self.slug = slugify(self.name)
        super(VintageRegion, self).save(*args, **kwargs)

class Vintage(models.Model):
    year = models.CharField(max_length=4, blank=False)
    region = models.ForeignKey(VintageRegion, on_delete=models.DO_NOTHING, blank=False)
    varietal = models.ForeignKey(VarietalBlend, on_delete=models.DO_NOTHING, null=True)
    score = models.IntegerField(blank=False)
    
    @property
    def region_name(self):
        return self.region.name
    @property
    def country(self):
        return [f for f in self.region.region.all()][0].country
    @property
    def mastervarietal_name(self):
        return [f for f in self.region.region.all()][0].country
    class Meta:
        unique_together = ['year','region','varietal']
    
    def __str__(self):
        return f"{self.year} {self.region.name} {self.varietal}"