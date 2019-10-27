#!/usr/bin/env python
from __future__ import print_function

import os
import sys

import django
from django.conf import settings


def _format_version(version_tuple):
    return ".".join(map(str, version_tuple))


def delete_migrations():
    from os.path import exists, abspath, dirname, join

    migrations_dir = join(
        dirname(abspath(__file__)), "django_enumfield", "tests", "migrations"
    )
    if exists(migrations_dir):
        os.system("rm -r " + migrations_dir)


def main():
    print(
        "Running tests for Python {} and Django {}".format(
            _format_version(sys.version_info[:3]), _format_version(django.VERSION[:3])
        )
    )
    import warnings

    # Ignore deprecation warning caused by Django on 3.7/3.8 + 2.0/2.1
    if sys.version_info[:2] in ((3, 7), (3, 8)) and django.VERSION[:2] in (
        (2, 0),
        (2, 1),
    ):
        module = r"(?!django).*"
    else:
        module = ""

    warnings.filterwarnings("error", module=module, category=DeprecationWarning)

    delete_migrations()

    if not settings.configured:
        # Dynamically configure the Django settings with the minimum necessary to
        # get Django running tests
        settings.configure(
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.admin",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django_enumfield",
                "django_enumfield.tests",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ]
                    },
                }
            ],
            # Django replaces this, but it still wants it. *shrugs*
            DATABASE_ENGINE="django.db.backends.sqlite3",
            DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3"}},
            MEDIA_ROOT="/tmp/django_enums/",
            MEDIA_PATH="/media/",
            ROOT_URLCONF="django_enumfield.tests.urls",
            DEBUG=True,
            TEMPLATE_DEBUG=True,
            MIDDLEWARE_CLASSES=[],
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
            ],
        )

    # Compatibility with Django 1.7's stricter initialization
    if hasattr(django, "setup"):
        django.setup()

    from django.test.utils import get_runner

    test_runner = get_runner(settings)(verbosity=2, interactive=True)
    if "--failfast" in sys.argv:
        test_runner.failfast = True

    failures = test_runner.run_tests(["django_enumfield"])

    delete_migrations()

    sys.exit(failures)


if __name__ == "__main__":
    main()
