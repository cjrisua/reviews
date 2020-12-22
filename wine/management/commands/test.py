from django.core.management.base import BaseCommand
from ...models import Country, Terroir
from .utils.__wine import WineUtils
import pandas as pd
from django.utils.text import slugify 

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        pass