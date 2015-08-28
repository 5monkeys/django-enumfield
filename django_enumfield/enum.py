from __future__ import absolute_import

from enum import Enum as NativeEnum

import logging

from django.utils import six

from django_enumfield.db.fields import EnumField


logger = logging.getLogger(__name__)


class BlankEnum(NativeEnum):
    BLANK = ''

    @property
    def label(self):
        return ''


class Enum(NativeEnum):
    """ A container for holding and restoring enum values """

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return super(Enum, self).__eq__(other)

    @property
    def values(self):
        return self.__members__

    @classmethod
    def choices(cls, blank=False):
        """ Choices for Enum
        :return: List of tuples (<value>, <human-readable value>)
        :rtype: list
        """
        choices = sorted([(member.value, member) for member in cls if not member.name.startswith('_')], key=lambda x: x[0])
        if blank:
            choices.insert(0, ('', BlankEnum.BLANK))
        return choices

    @classmethod
    def default(cls):
        """ Default Enum value. Override this method if you need another default value.
        Usage:
            IntegerField(choices=my_enum.choices(), default=my_enum.default(), ...
        :return Default value, which is the first one by default.
        :rtype: int
        """
        return tuple(cls)[0]

    @classmethod
    def field(cls, **kwargs):
        """ A shortcut for field declaration
        Usage:
            class MyModelStatuses(Enum):
                UNKNOWN = 0

            class MyModel(Model):
                status = MyModelStatuses.field()

        :param kwargs: Arguments passed in EnumField.__init__()
        :rtype: EnumField
        """
        return EnumField(cls, **kwargs)

    @classmethod
    def get(cls, name_or_numeric):
        """ Get Enum.Value object matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int or str
        :rtype: Enum.Value
        """
        if isinstance(name_or_numeric, six.text_type):
            for member in cls:
                if six.text_type(member.name) == name_or_numeric:
                    return member
            return None

        return name_or_numeric

    @property
    def label(self):
        """ Get human readable label for the matching Enum.Value.
        :param numeric: Enum value
        :type numeric: int
        :return: label for value
        :rtype: str or
        """
        labels = getattr(self.__class__, 'labels', None)
        if labels is None:
            return six.text_type(self.name)

        return six.text_type(self.__class__.value.get(self.value, self.name))

    @classmethod
    def items(cls):
        """
        :return: List of tuples consisting of every enum value in the form [('NAME', value), ...]
        :rtype: list
        """
        return [item for item in cls.__members__.items() if not item[0].startswith('_')]

    @classmethod
    def is_valid_transition(cls, from_value, to_value):
        """ Will check if to_value is a valid transition from from_value. Returns true if it is a valid transition.
        :param from_value: Start transition point
        :param to_value: End transition point
        :type from_value: int
        :type to_value: int
        :return: Success flag
        :rtype: bool
        """
        try:
            return from_value == to_value or from_value in cls.transition_origins(to_value)
        except KeyError:
            return False

    @classmethod
    def transition_origins(cls, to_value):
        """ Returns all values the to_value can make a transition from.
        :param to_value End transition point
        :type to_value: int
        :rtype: list
        """
        return cls._transitions.value[to_value]
