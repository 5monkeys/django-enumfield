# django-enumfield

Provides an enumeration Django model field (using `IntegerField`) with reusable enums and transition validation.

[![Build Status](https://travis-ci.org/5monkeys/django-enumfield.svg?branch=master)](https://travis-ci.org/5monkeys/django-enumfield)
[![PyPi Version](https://img.shields.io/pypi/v/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
[![License](https://img.shields.io/pypi/l/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
[![Wheel](https://img.shields.io/pypi/wheel/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)


Installation
------------

Currently, [we test](https://travis-ci.org/5monkeys/django-enumfield) Django versions 1.11-2.2 and Python versions 2.7, 3.4-3.7.

Install `django-enumfield` in your Python environment:

```sh
$ pip install django-enumfield
```

For use with Django versions prior to 1.8 use version 
[`1.2.1`](https://github.com/5monkeys/django-enumfield/tree/1.2.1)

For use with Django versions prior to 1.11 use version 
[`1.5`](https://github.com/5monkeys/django-enumfield/tree/1.5)

Usage
-----

Create an `Enum`-class and pass it as first argument to the Django model `EnumField`.

```python
from django.db import models
from django_enumfield import enum


class BeerStyle(enum.Enum):
    LAGER = 0
    STOUT = 1
    WEISSBIER = 2


class Beer(models.Model):
    style = enum.EnumField(BeerStyle, default=BeerStyle.LAGER)
    

# Use .get to get enum values from either name or ints
BeerStyle.get("LAGER")  # <BeerStyle.LAGER: 0>
BeerStyle.get(1)  # <BeerStyle.STOUT: 1>
BeerStyle.get(BeerStyle.WEISSBIER)  # <BeerStyle.WEISSBIER: 2>, of course

# It's also possible to use the normal enum way to get the value
BeerStyle(1)  # <BeerStyle.STOUT: 1>
BeerStyle["LAGER"]  # <BeerStyle.LAGER: 0>
```

You can also set default value on your enum class using `__default__`
attribute

```python
from django.db import models
from django_enumfield import enum


class BeerStyle(enum.Enum):
    LAGER = 0
    STOUT = 1
    WEISSBIER = 2

    __default__ = LAGER


class Beer(models.Model):
    style_default_lager = enum.EnumField(BeerStyle)
    style_default_stout = enum.EnumField(BeerStyle, default=BeerStyle.STOUT)
    

# When you set __default__ attribute, you can access default value via
# `.default()` method of your enum class
assert BeerStyle.default() == BeerStyle.LAGER

Beer.objects.create(style=BeerStyle.STOUT)
Beer.objects.filter(style=BeerStyle.STOUT)
```

You can use your own labels for `Enum` items

```python
from django_enumfield import enum


class Animals(enum.Enum):
    CAT = 1
    DOG = 2

    __labels__ = {
        CAT: "Cat",
        DOG: "Dog"
    }
```

The `Enum`-class provides the possibility to use transition validation.

```python
from django.db import models
from django_enumfield import enum
from django_enumfield.exceptions import InvalidStatusOperationError


class PersonStatus(enum.Enum):
    ALIVE = 1
    DEAD = 2
    REANIMATED = 3

    __transitions__ = {
        DEAD: (ALIVE,),
        REANIMATED: (DEAD,)
    }


class Person(models.Model):
    status = enum.EnumField(PersonStatus)

# These transitions state that a PersonStatus can only go to DEAD from ALIVE and to REANIMATED from DEAD.
person = Person.objects.create(status=PersonStatus.ALIVE)
try:
    person.status = PersonStatus.REANIMATED
except InvalidStatusOperationError:
    print("Person status can not go from ALIVE to REANIMATED")
else:
    # All good
    person.save()
```

The `Enum`-class can also be used without the `EnumField`. This is very useful in Django form `ChoiceField`s.

```python
from django import forms
from django_enumfield import enum


class GenderEnum(enum.Enum):
    MALE = 1
    FEMALE = 2

    __labels__ = {
        MALE: "Male",
        FEMALE: "Female",
    }


class PersonForm(forms.Form):
    gender = forms.TypedChoiceField(choices=GenderEnum.choices(), coerce=int)
```

Rendering `PersonForm` in a template will generate a select-box with "Male" and "Female" as option labels for the gender field.


Local Development Environment
-----------------------------

Make sure black and isort is installed in your env with `pip install -e .[dev]`.

Before committing run `make format` to apply black and isort to all files to keep.
