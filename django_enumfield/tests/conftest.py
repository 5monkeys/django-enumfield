import os
from pathlib import Path

import django
import pytest

SECRET_KEY = "secret"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_enumfield",
    "django_enumfield.tests",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,  # Raise template errors
        },
    }
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
ROOT_URLCONF = "django_enumfield.tests.urls"
DEBUG = True
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


def pytest_configure(config):
    from django.conf import settings

    settings.configure(
        SECRET_KEY=SECRET_KEY,
        INSTALLED_APPS=INSTALLED_APPS,
        TEMPLATES=TEMPLATES,
        DATABASES=DATABASES,
        ROOT_URLCONF=ROOT_URLCONF,
        DEBUG=DEBUG,
        MIDDLEWARE=MIDDLEWARE,
    )

    django.setup()


@pytest.fixture(scope="session", autouse=True)
def delete_migrations():
    migrations_dir = Path(__file__).parent / "migrations"
    if migrations_dir.exists() and migrations_dir.is_dir():
        os.system("rm -r " + str(migrations_dir))

    yield

    if migrations_dir.exists() and migrations_dir.is_dir():
        os.system("rm -r " + str(migrations_dir))
