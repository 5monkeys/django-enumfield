from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_enumfield.db.fields import EnumField
from django_enumfield.enum import Enum


class LampState(Enum):
    OFF = 0
    ON = 1


class Lamp(models.Model):
    state = EnumField(LampState)


class PersonStatus(Enum):
    UNBORN = 0
    ALIVE = 1
    DEAD = 2
    REANIMATED = 3
    VOID = 4

    _transitions = {
        UNBORN: (VOID,),
        ALIVE: (UNBORN,),
        DEAD: (UNBORN, ALIVE),
        REANIMATED: (DEAD,)
    }


class Person(models.Model):
    example = models.CharField(max_length=100, default='foo')
    status = EnumField(PersonStatus, default=PersonStatus.ALIVE)

    def save(self, *args, **kwargs):
        super(Person, self).save(*args, **kwargs)
        return 'Person.save'


class BeerStyle(Enum):
    LAGER = 0
    STOUT = 1
    WEISSBIER = 2


class BeerState(Enum):
    FIZZY = 0
    STALE = 1
    EMPTY = 2


class Beer(models.Model):
    style = EnumField(BeerStyle)
    state = EnumField(BeerState, null=True, blank=True)


class LabelBeer(Enum):
    STELLA = 0
    JUPILER = 1
    TYSKIE = 2

    labels = {
        STELLA: _('Stella Artois'),
        TYSKIE: _('Browar Tyskie'),
    }
