from __future__ import absolute_import

import logging
from enum import Enum as NativeEnum, IntEnum as NativeIntEnum
from typing import Callable, Sequence, Dict, Optional, Type, Union, cast, overload

from django.utils import six
from django.utils.decorators import classproperty

from django_enumfield.db.fields import EnumField

logger = logging.getLogger(__name__)
RAISE = object()


class BlankEnum(NativeEnum):
    BLANK = ""

    @property
    def label(self):
        return ""


def classdispatcher(class_method):
    class _classdispatcher(object):
        def __init__(self, method=None):
            self.fget = method

        def __get__(self, instance, cls=None):
            if instance is None:
                return getattr(cls, class_method)
            return self.fget(instance)

    return _classdispatcher


class Enum(NativeIntEnum):
    """ A container for holding and restoring enum values """

    __labels__ = {}  # type: Dict[Union[Enum, int], six.text_type]
    __default__ = None  # type: Optional[Union[Enum, int]]
    __transitions__ = {}  # type: Dict[Union[Enum, int], Sequence[Union[Enum, int]]]

    @classdispatcher("get_name")
    def name(self):
        # type: () -> str
        return self._name_

    @classdispatcher("get_label")
    def label(self):
        # type: () -> str
        return self._label

    @classproperty
    def do_not_call_in_templates(cls):
        # Fix for Django templates so that any lookups of enums won't fail
        # More info: https://stackoverflow.com/questions/35953132/how-to-access-enum-types-in-django-templates  # noqa: E501
        return True

    @classproperty
    def values(cls):
        return {member.value: member for member in cls}

    @property
    def _label(self):
        """ Get human readable label for the matching Enum.Value.
        :return: label for value
        :rtype: str
        """
        label = self.__class__.__labels__.get(self.value, self.name)
        return six.text_type(label)

    def deconstruct(self):
        """
        See "Adding a deconstruct() method" in
        https://docs.djangoproject.com/en/1.8/topics/migrations/
        """
        c = self.__class__
        path = "{}.{}".format(c.__module__, c.__name__)
        return path, [self.value], {}

    @classmethod
    def items(cls):
        """
        :return: List of tuples consisting of every enum value in the form
            [('NAME', value), ...]
        :rtype: list
        """
        items = [(member.name, member.value) for member in cls]
        return sorted(items, key=lambda x: x[1])

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
    def get(cls, name_or_numeric, default=None):
        """ Get Enum.Value object matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int or str
        :param default: The default to return if the value passed is not
            a valid enum value
        :type default: Any
        :rtype: Enum.Value
        """
        if isinstance(name_or_numeric, cls):
            return name_or_numeric

        if isinstance(name_or_numeric, int):
            try:
                return cls(name_or_numeric)
            except ValueError:
                pass
        elif isinstance(name_or_numeric, six.string_types):
            try:
                return cls[name_or_numeric]
            except KeyError:
                pass

        return default

    @classmethod
    def get_name(cls, name_or_numeric):
        """ Get Enum.Value name matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int or str
        :return: The name or None if not found
        """
        value = cls.get(name_or_numeric)
        if value is not None:
            return value.name

    @classmethod
    def get_label(cls, name_or_numeric):
        """ Get Enum.Value label matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int or str
        :return: The label or None if not found
        """
        value = cls.get(name_or_numeric)
        if value is not None:
            return value._label

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

        return (
            from_value == to_value
            or not cls.__transitions__
            or (from_value in cls.transition_origins(to_value))
        )

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
