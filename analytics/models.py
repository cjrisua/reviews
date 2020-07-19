from django.db import models
from jsonfield import JSONField
from wine.models import Wine, Review

DEFAULT_ID = -1
class ParkerSomm(models.Model):
    TRAIN_TYPE = models.TextChoices = (
        ('NULL','NULL'),
        ("WINENAME","WINENAME"), 
        ("REVIEW","REVIEW"),
    )
    keywords = JSONField()
    metadata = JSONField()
    sourceid = models.IntegerField(blank=False, default=0)
    sourcetype = models.CharField(choices=TRAIN_TYPE,max_length=25, default='NULL')

    def __str__(self):
        return self.keywords
    class Meta:
        unique_together = ['keywords', 'sourceid', 'sourcetype']
        ordering = ['-id']