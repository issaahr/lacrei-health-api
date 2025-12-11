import os

import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# API Key vazia = middleware permite acesso sem validação
os.environ['API_KEY'] = ''


def pytest_configure():
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    django.setup()
