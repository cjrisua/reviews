from django.db import models
from django.utils.text import slugify
from jsonfield import JSONField
from django.utils.text import slugify


class Varietal(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=150)
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
    slug = models.CharField(max_length=150, blank=False, null=False, default='')
    class Meta:
        ordering = ('-name',)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Country, self).save(*args, **kwargs)

class Terroir(models.Model):
    country = models.ForeignKey(Country, blank='True', null=True, on_delete=models.CASCADE, default=-1)
    parentterroir = models.ForeignKey('self', blank='True', null=True, related_name='subterroir', on_delete=models.CASCADE, default=-1)
    name = models.CharField(max_length=150)
    isappellation = models.BooleanField(default=False)
    isvineyard = models.BooleanField(default=False)
    slug = models.CharField(max_length=150, blank=False, null=False, default='')
    class Meta:
        unique_together = ['country', 'slug', 'parentterroir']
        ordering = ('country','slug')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Terroir, self).save(*args, **kwargs)

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

class BlendVarietal(models.Model):
    name = models.CharField(max_length=150)
    varietal = models.ManyToManyField(Varietal)

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

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
    producer = models.ForeignKey(Producer, related_name='wines', on_delete=models.CASCADE)
    terroir = models.ForeignKey(Terroir, on_delete=models.PROTECT)
    varietal = models.ForeignKey(BlendVarietal, on_delete=models.PROTECT, blank=False)
    name = models.CharField(max_length=150)
    wtype = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['producer', 'name']
        ordering = ['name']

class Critic(models.Model):
     name = models.CharField(max_length=50)

     def __str__(self):
        return self.name

class Market(models.Model):
    wine =  models.ForeignKey(Wine, related_name='vintage',  on_delete=models.CASCADE, blank=False, default=None)
    varietal = models.ForeignKey(BlendVarietal, on_delete=models.PROTECT)
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