import pandas as pd
from django.conf import settings
import django

settings.configure(
    DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2',
    DATABASE_NAME = 'wino',
    DATABASE_USER = 'vinomio',
    DATABASE_PASSWORD = '4`^B]T8:NqyAh2xp',
    DATABASE_HOST = 'localhost',
    DATABASE_PORT = '5432',
    TIME_ZONE = 'America/New_York',
)
django.setup()
from wine.models import Producer