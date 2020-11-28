from django.db import models
from django.utils.text import slugify
from jsonfield import JSONField
from django.utils.text import slugify


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

class Terroir(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_region')
    parentterroir = models.ForeignKey('self', blank='True', null=True, related_name='subterroir', on_delete=models.CASCADE, default=-1)
    name = models.CharField(max_length=150)
    isappellation = models.BooleanField(default=False)
    isvineyard = models.BooleanField(default=False)
    slug = models.CharField(max_length=150, blank=False, null=False, default='')
    
    class Meta:
        unique_together = ['country', 'slug', 'parentterroir']
        ordering = ('country','parentterroir__id','slug')

    @staticmethod
    def traverse_terroir(self, terroir, name):
        if terroir.parentterroir is not None:
            name = Terroir.traverse_terroir(self, terroir.parentterroir, f'{terroir.parentterroir.name} > {name}')
        else:
           self.__traversed_name = name
    
    @property
    def region_traverse(self): 
        region_names = Terroir.traverse_terroir(self, self.parentterroir,f'{self.parentterroir.name} > {self.name}')
        return self.__traversed_name

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Terroir, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.__traversed_name = None

        super().__init__(*args, **kwargs)

class Producer(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(unique=True, max_length=150, blank=False, null=False, default='')

    class Meta:
        ordering = ('-name',)
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Producer, self).save(*args, **kwargs)

class MasterVarietal(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.CharField(unique=True, max_length=150, blank=False, null=False, default='')

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
    COUNTRY = models.TextChoices = (
        ('FRA','France'),
        ('NZL','New Zealand'),
        ('AUS','Australia'),
        ('CHL','Chile'),
        ('ARG','Argentina'),
        ('USA','United States'),
        ('PRT','Portugal'),
        ('ESP','Spain'),
        ('ITA','Italy'),
        ('HUN','Hungary'),
        ('DEU','Germany'),
        ('AUT','Austria'),
        ('CAN', 'Canada'),
        ('ISR','Israel'),
        ('ZAF', 'South Africa'),
    )
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
    producer = models.ForeignKey(Producer, related_name='wines', on_delete=models.CASCADE)
    terroir = models.ForeignKey(Terroir, on_delete=models.PROTECT)
    varietal = models.ForeignKey(VarietalBlend, on_delete=models.PROTECT, blank=False)
    name = models.CharField(max_length=150)
    wtype =  models.CharField(
        max_length=4,
        choices=WINETYPE,
    )

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
    def vintages_indexing(self):

        """Wine for indexing.
        Used in Elasticsearch indexing.
        """
        print(f'adding vintages_indexing...pk {self.id}')
        if self.name is not None:
            return [v.year for v in Market.objects.filter(wine__id=self.id)]

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