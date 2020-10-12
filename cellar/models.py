from django.db import models
from django.urls import reverse
from wine.models import Producer, Wine, Market
from django.utils import timezone
from django.contrib.auth.models import User

COLLECTION_CHOICES = (
        ('added', 'Added'),
        ('pending', 'Pending Delivery'),
        ('drunk', 'Drunk'),
        ('curated','Curated'),
        ('removed', 'Removed'),
    )
ALLOCATION_CHOICES = (
    ('waiting', 'Waiting'),
    ('active', 'Active'),
    ('atfault','At Fault'),
)
class ActiveAllocationManager(models.Manager):
    def get_queryset(self):
        return super(ActiveAllocationManager,self).get_queryset().filter(status='active')

class Allocation(models.Model):
    producer = models.ForeignKey(Producer,  on_delete=models.CASCADE, related_name="producer", unique=True)
    signupdate = models.DateField()
    addeddate = models.DateField(default='1900-01-01',blank=True)
    mailingmonths = models.CharField(max_length=50, default='',  blank=True)
    lastpurchasedate = models.DateField(default='1900-01-01',blank=True)
    status = models.CharField(max_length=15, choices = ALLOCATION_CHOICES, blank=True, default='waiting')
    inactivitypenalty = models.BooleanField(default=True,blank=True)
    #active = ActiveAllocationManager()

    def __str__(self):
        return self.producer.name

    def get_absolute_url(self):
        return reverse('cellar:allocation',)

class Cellar(models.Model):
    name = models.CharField(max_length=50, default="My Cellar")
    location = models.CharField(max_length=50)
    capacity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Curator(models.Model):
    curator = models.ForeignKey(User, on_delete=models.CASCADE)
    cellar = models.ForeignKey(Cellar, on_delete=models.CASCADE, related_name="user_cellars")

    def __str__(self):
        return self.curator.email

class Location(models.Model):
    location = models.CharField(max_length=50)
    cellar = models.ForeignKey(Cellar, on_delete=models.CASCADE, related_name="cellar_partitions")
    class Meta:
        ordering = ('-location',)
    def __str__(self):
        return self.location

class Collection(models.Model):
    collectible = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="wine_market")
    storage = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="storage")
    cellar = models.ForeignKey(Cellar, on_delete=models.CASCADE, related_name="cellar_collection")
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=COLLECTION_CHOICES,
                              default='added')
    class Meta:
        ordering = ('-collectible',)
    
    def __str__(self):
        return self.collectible.__str__()
    
    def get_absolute_url(self):
        return reverse('wine:wine_detail',
                       args=[self.collectible.producerslug,
                             self.collectible.year,
                             self.collectible.wineslug])