# django-enumfield

Provides an enumeration Django model field (using `IntegerField`) with reusable enums and transition validation.

[![Build Status](https://github.com/5monkeys/django-enumfield/workflows/Test/badge.svg)](https://github.com/5monkeys/django-enumfield/actions)
[![PyPi Version](https://img.shields.io/pypi/v/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
[![License](https://img.shields.io/pypi/l/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
[![Wheel](https://img.shields.io/pypi/wheel/django-enumfield.svg)](https://pypi.python.org/pypi/django-enumfield)
![Coveralls github](https://img.shields.io/coveralls/github/5monkeys/django-enumfield)

Installation
------------

Currently, [we test](https://github.com/5monkeys/django-enumfield/actions) Django versions 2.2-4.0 and Python versions 3.7-3.10.

Install `django-enumfield` in your Python environment:

```sh
$ pip install django-enumfield
```

**Upgrading from django-enumfield 1.x?** [See the migration guide](docs/migrate-to-20.md)

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
print(BeerStyle.get("LAGER"))  # <BeerStyle.LAGER: 0>
print(BeerStyle.get(1))  # <BeerStyle.STOUT: 1>
print(BeerStyle.get(BeerStyle.WEISSBIER))  # <BeerStyle.WEISSBIER: 2>

# It's also possible to use the normal enum way to get the value
print(BeerStyle(1))  # <BeerStyle.STOUT: 1>
print(BeerStyle["LAGER"])  # <BeerStyle.LAGER: 0>

# The enum value has easy access to their value and name
print(BeerStyle.LAGER.value)  # 0
print(BeerStyle.LAGER.name)  # "LAGER"
```

For more information about Python 3 enums
(which our `Enum` inherits, `IntEnum` to be specific)
checkout the [docs](https://docs.python.org/3/library/enum.html).


### Setting the default value

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


class BeerStyleNoDefault(enum.Enum):
    LAGER = 0


class Beer(models.Model):
    style_default_lager = enum.EnumField(BeerStyle)
    style_default_stout = enum.EnumField(BeerStyle, default=BeerStyle.STOUT)
    style_default_null = enum.EnumField(BeerStyleNoDefault, null=True, blank=True)


# When you set __default__ attribute, you can access default value via
# `.default()` method of your enum class
assert BeerStyle.default() == BeerStyle.LAGER

beer = Beer.objects.create()
assert beer.style_default_larger == BeerStyle.LAGER
assert beer.style_default_stout == BeerStyle.STOUT
assert beer.style_default_null is None
```

### Labels

You can use your own labels for `Enum` items

```python
from django.utils.translation import gettext_lazy
from django_enumfield import enum


class Animals(enum.Enum):
    CAT = 1
    DOG = 2
    SHARK = 3

    __labels__ = {
        CAT: gettext_lazy("Cat"),
        DOG: gettext_lazy("Dog"),
    }


print(Animals.CAT.label)  # "Cat"
print(Animals.SHARK.label)  # "SHARK"

# There's also classmethods for getting the label
print(Animals.get_label(2))  # "Dog"
print(Animals.get_label("DOG"))  # "Dog"
```

### Validate transitions

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
        DEAD: (ALIVE,),  # Can go from ALIVE to DEAD
        REANIMATED: (DEAD,)  # Can go from DEAD to REANIMATED
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

### In forms

The `Enum`-class can also be used without the `EnumField`. This is very useful in Django form `ChoiceField`s.

```python
from django import forms
from django_enumfield import enum
from django_enumfield.forms.fields import EnumChoiceField


class GenderEnum(enum.Enum):
    MALE = 1
    FEMALE = 2

    __labels__ = {
        MALE: "Male",
        FEMALE: "Female",
    }


class PersonForm(forms.Form):
    gender = EnumChoiceField(GenderEnum)
```

Rendering `PersonForm` in a template will generate a select-box with "Male" and "Female" as option labels for the gender field.


Local Development Environment
-----------------------------

Make sure black and isort is installed in your env with `pip install -e .[dev]`.

Before committing run `make format` to apply black and isort to all files.
