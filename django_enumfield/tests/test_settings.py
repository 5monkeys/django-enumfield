import os
import django

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

if django.VERSION[:2] >= (1, 3):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }
else:
    DATABASE_ENGINE = 'sqlite3'
    CACHE_BACKEND = 'locmem://'

INSTALLED_APPS = [
    'django_enumfield',
    'tests.models'
]


SECRET_KEY = "iufoj=mibkpdz*%bob952x(%49rqgv8gg45k36kjcg76&-y5=!"
