from django.db import models
from django.utils.text import slugify

class Producer(models.Model):
    name = models.CharField(max_length=150)

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
        ('ITA','Italy')
    )
    producer = models.ForeignKey(Producer, related_name='wines', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    country = models.CharField(choices=COUNTRY,max_length=3)
    region = models.CharField(max_length=255)
    terroir = models.CharField(max_length=125)

    class Meta:
        ordering = ('-producer',)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['producer', 'id']
        ordering = ['name']

class Critic(models.Model):
     name = models.CharField(max_length=50)

     def __str__(self):
        return self.name

class Market(models.Model):
    wine =  models.ForeignKey(Wine, related_name='vintage',  on_delete=models.CASCADE, blank=False, default=None)
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