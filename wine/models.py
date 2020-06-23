from django.db import models

class Producer(models.Model):
    name = models.CharField(max_length=150)

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
        ('ITA','Italy')
    )
    producer = models.ForeignKey(Producer, related_name='wines', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    country = models.CharField(choices=COUNTRY,max_length=3)
    region = models.CharField(max_length=255)
    terroir = models.CharField(max_length=125)

    class Meta:
        unique_together = ['producer', 'id']
        ordering = ['name']

class Critic(models.Model):
     name = models.CharField(max_length=50)

class Market(models.Model):
    wine =  models.ForeignKey(Wine, related_name='vintage',  on_delete=models.CASCADE, blank=False, default=None)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    year = models.CharField(max_length=4, blank=False)
    reviews = models.ManyToManyField(Critic, through='Review', blank=True)
    
class Review(models.Model):
    critic = models.ForeignKey(Critic,on_delete=models.CASCADE)
    market =  models.ForeignKey(Market,on_delete=models.CASCADE)
    issuedate = models.DateField(blank=False)
    observation = models.TextField()
    score = models.IntegerField(default=0)
    

    
