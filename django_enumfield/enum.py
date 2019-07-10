from __future__ import absolute_import

import logging
from enum import Enum as NativeEnum, IntEnum as NativeIntEnum

from django.utils import six
from django.utils.translation import ugettext

from django_enumfield.db.fields import EnumField
from django_enumfield.exceptions import InvalidStatusOperationError

logger = logging.getLogger(__name__)


class BlankEnum(NativeEnum):
    BLANK = ""

    @property
    def label(self):
        return ""


class Enum(NativeIntEnum):
    """ A container for holding and restoring enum values """

    __labels__ = {}
    __default__ = None
    __transitions__ = {}

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

    def __hash__(self):
        path, (val,), _ = self.deconstruct()
        return hash("{}.{}".format(path, val))

    def deconstruct(self):
        """
        See "Adding a deconstruct() method" in
        https://docs.djangoproject.com/en/1.8/topics/migrations/
        """
        c = self.__class__
        path = "{}.{}".format(c.__module__, c.__name__)
        return path, [self.value], {}

    @classmethod
    def choices(cls, blank=False):
        """ Choices for Enum
        :return: List of tuples (<value>, <member>)
        :rtype: list
        """
        choices = sorted([(member.value, member) for member in cls], key=lambda x: x[0])
        if blank:
            choices.insert(0, (BlankEnum.BLANK.value, BlankEnum.BLANK))
        return choices

    @classmethod
    def default(cls):
        """ Default Enum value. Set default value to `__default__` attribute
        of your enum class or override this method if you need another
        default value.
        Usage:
            IntegerField(choices=my_enum.choices(), default=my_enum.default(), ...
        :return Default value, which is the first one by default.
        :rtype: enum member
        """
        if cls.__default__ is not None:
            return cls(cls.__default__)

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
        if isinstance(name_or_numeric, six.string_types):
            if name_or_numeric.isdigit():
                name_or_numeric = int(name_or_numeric)

        if isinstance(name_or_numeric, six.text_type):
            for member in cls:
                if six.text_type(member.name) == name_or_numeric:
                    return member

        elif isinstance(name_or_numeric, int):
            for member in cls:
                if int(member.value) == name_or_numeric:
                    return cls(name_or_numeric)

        elif isinstance(name_or_numeric, cls):
            return name_or_numeric

        raise InvalidStatusOperationError(
            ugettext(
                six.text_type(
                    "{value!r} is not one of the available choices for enum {enum}."
                )
            ).format(value=name_or_numeric, enum=cls)
        )

    @property
    def label(self):
        """ Get human readable label for the matching Enum.Value.
        :return: label for value
        :rtype: str
        """
        label = self.__class__.__labels__.get(self.value, self.name)
        return six.text_type(label)

    @classmethod
    def is_valid_transition(cls, from_value, to_value):
        """ Will check if to_value is a valid transition from from_value.
        Returns true if it is a valid transition.

        :param from_value: Start transition point
        :param to_value: End transition point
        :type from_value: int
        :type to_value: int
        :return: Success flag
        :rtype: bool
        """
        if isinstance(from_value, cls):
            from_value = from_value.value

        if isinstance(to_value, cls):
            to_value = to_value.value
        try:
            return (
                from_value == to_value
                or not cls.__transitions__
                or (from_value in cls.transition_origins(to_value))
            )
        except KeyError:
            return False

    @classmethod
    def transition_origins(cls, to_value):
        """ Returns all values the to_value can make a transition from.
        :param to_value End transition point
        :type to_value: int
        :rtype: list
        """
        if isinstance(to_value, cls):
            to_value = to_value.value
        return cls.__transitions__.get(to_value, [])
