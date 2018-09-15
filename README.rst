django-enumfield
================

Provides an enumeration Django model field (using IntegerField) with reusable enums and transition validation.

.. image:: https://travis-ci.org/5monkeys/django-enumfield.svg?branch=master
        :target: http://travis-ci.org/5monkeys/django-enumfield

.. image:: https://img.shields.io/pypi/v/django-enumfield.svg
    :target: https://pypi.python.org/pypi/django-enumfield

.. image:: https://img.shields.io/pypi/l/django-enumfield.svg
    :target: https://pypi.python.org/pypi/django-enumfield

.. image:: https://img.shields.io/pypi/pyversions/django-enumfield.svg
    :target: https://pypi.python.org/pypi/django-enumfield

.. image:: https://img.shields.io/pypi/wheel/django-enumfield.svg
    :target: https://pypi.python.org/pypi/django-enumfield


Installation
------------

Currently, `we test`__ Django versions 1.8-2.1 and Python versions 2.7,3.4-3.7.

Install ``django-enumfield`` in your Python environment:

.. _travis: https://travis-ci.org/5monkeys/django-enumfield

__ travis_

.. code:: sh

    $ pip install django-enumfield

For use with Django versions prior to 1.8 do this

.. code:: sh

    $ pip install django-enumfield==1.2.1

If you are looking for native ``enum`` (or enum34_) support, try testing
`Pull Request #26`__ which is planned for Django 1.10+.

.. _pr26: https://github.com/5monkeys/django-enumfield/pull/26

__ pr26_

.. _enum34: https://pypi.python.org/pypi/enum34


Usage
-----

Create an Enum-class and pass it as first argument to the Django model EnumField.

.. code:: python

    from django.db import models
    from django_enumfield import enum

    class BeerStyle(enum.Enum):
        LAGER = 0
        STOUT = 1
        WEISSBIER = 2

    class Beer(models.Model):
        style = enum.EnumField(BeerStyle, default=BeerStyle.LAGER)

.. code:: python

    Beer.objects.create(style=BeerStyle.STOUT)
    Beer.objects.filter(style=BeerStyle.STOUT)

You can use your own labels for Enum items

.. code:: python

    class Animals(enum.Enum):
        CAT = 1
        DOG = 2

        labels = {
            CAT: 'Cat',
            DOG: 'Dog'
        }

The Enum-class provides the possibility to use transition validation.

.. code:: python

    from django.db import models
    from django_enumfield import enum

    class PersonStatus(enum.Enum):
        ALIVE = 1
        DEAD = 2
        REANIMATED = 3

        _transitions = {
            DEAD: (ALIVE,),
            REANIMATED: (DEAD,)
        }

    class Person(models.Model):
        status = enum.EnumField(PersonStatus)

These transitions state that a PersonStatus can only go to DEAD from ALIVE and to REANIMATED from DEAD.

.. code:: python

    person = Person.objects.create(status=PersonStatus.ALIVE)
    try:
        person.status = PersonStatus.REANIMATED
        person.save()
    except InvalidStatusOperationError:
        print("Person status can not go from ALIVE to REANIMATED")

The Enum-class can also be used without the EnumField. This is very useful in Django form ChoiceFields.

.. code:: python

    from django.forms import Form
    from django_enumfield import enum

    class GenderEnum(enum.Enum):
        MALE = 1
        FEMALE = 2

        labels = {
            MALE: 'Male',
            FEMALE: 'Female',
        }

    class PersonForm(forms.Form)
        gender = forms.TypedChoiceField(choices=GenderEnum.choices(), coerce=int)

Rendering PersonForm in a template will generate a select-box with "Male" and "Female" as option labels for the gender field.
