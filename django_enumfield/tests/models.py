from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_enumfield.db.fields import EnumField
from django_enumfield.enum import Enum


class LampState(Enum):
    OFF = 0
    ON = 1

    __default__ = OFF


class Lamp(models.Model):
    state = EnumField(LampState, verbose_name="stately_state")


class PersonStatus(Enum):
    UNBORN = 0
    ALIVE = 1
    DEAD = 2
    REANIMATED = 3
    VOID = 4

    __transitions__ = {
        UNBORN: (VOID,),
        ALIVE: (UNBORN,),
        DEAD: (UNBORN, ALIVE),
        REANIMATED: (DEAD,),
    }


class PersonStatusDefault(Enum):
    UNBORN = 0
    ALIVE = 1
    DEAD = 2
    REANIMATED = 3
    VOID = 4

    __default__ = UNBORN


class Person(models.Model):
    example = models.CharField(max_length=100, default="foo")
    status = EnumField(PersonStatus, default=PersonStatus.ALIVE)

    def save(self, *args, **kwargs):
        super(Person, self).save(*args, **kwargs)
        return "Person.save"


class BeerStyle(Enum):
    LAGER = 0
    STOUT = 1
    WEISSBIER = 2

    __default__ = LAGER


class BeerState(Enum):
    FIZZY = 0
    STALE = 1
    EMPTY = 2

    __default__ = FIZZY


class LabelBeer(Enum):
    STELLA = 0
    JUPILER = 1
    TYSKIE = 2

    __labels__ = {STELLA: _("Stella Artois"), TYSKIE: _("Browar Tyskie")}


def get_default_beer_label():
    return LabelBeer.JUPILER


class Beer(models.Model):
    style = EnumField(BeerStyle)
    state = EnumField(BeerState, null=True, blank=True)
    label = EnumField(LabelBeer, default=get_default_beer_label)
