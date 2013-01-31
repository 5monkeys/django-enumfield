from django.db import models
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

    _transitions = {
        UNBORN: (),
        ALIVE: (UNBORN,),
        DEAD: (UNBORN, ALIVE),
        REANIMATED: (DEAD,)
    }


class Person(models.Model):
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
    state = EnumField(BeerState, null=True, db_index=False)
