from __future__ import absolute_import

import logging
import enum
from typing import (
    Any,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    Mapping,
    TYPE_CHECKING,
)
from django.utils.encoding import force_str

if TYPE_CHECKING:
    from django.utils.functional import _StrOrPromise as StrOrPromise

try:
    from django.utils.functional import classproperty  # type: ignore
except ImportError:
    # Pre-Django 3.1
    from django.utils.decorators import classproperty

from django_enumfield.db.fields import EnumField

__all__ = ("Enum", "EnumField")

logger = logging.getLogger(__name__)
RAISE = object()


class BlankEnum(enum.Enum):
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


Default = TypeVar("Default")
T = TypeVar("T", bound="Enum")


class Enum(enum.IntEnum):
    """A container for holding and restoring enum values"""

    __labels__ = {}  # type: Mapping[int, StrOrPromise]
    __default__ = None  # type: Optional[int]
    __transitions__ = {}  # type: Mapping[int, Sequence[int]]

    def __str__(self):
        return self.label

    @classdispatcher("get_name")
    def name(self):
        # type: () -> str
        return self._name_

    @classdispatcher("get_label")
    def label(self):
        # type: () -> str
        """Get human readable label for the matching Enum.Value.
        :return: label for value
        :rtype: str
        """
        labels = self.__class__.__labels__
        return force_str(labels.get(self.value, self.name))

    @classproperty  # type: ignore[arg-type]
    def do_not_call_in_templates(cls):
        # type: () -> bool
        # Fix for Django templates so that any lookups of enums won't fail
        # More info: https://stackoverflow.com/questions/35953132/how-to-access-enum-types-in-django-templates  # noqa: E501
        return True

    @classproperty  # type: ignore[arg-type]
    def values(cls):
        # type: () -> Mapping[int, Enum]
        return {member.value: member for member in cls}  # type: ignore[attr-defined]

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
        # type: () -> List[Tuple[str, int]]
        """
        :return: List of tuples consisting of every enum value in the form
            [('NAME', value), ...]
        """
        items = [(member.name, member.value) for member in cls]
        return sorted(items, key=lambda x: x[1])

    @classmethod
    def choices(cls, blank=False):
        # type: (bool) -> List[Tuple[Union[int, str], enum.Enum]]
        """Choices for Enum
        :return: List of tuples (<value>, <member>)
        """
        choices = sorted(
            [(member.value, member) for member in cls], key=lambda x: x[0]
        )  # type: List[Tuple[Union[str, int], enum.Enum]]
        if blank:
            choices.insert(0, (BlankEnum.BLANK.value, BlankEnum.BLANK))
        return choices

    @classmethod
    def default(cls):
        # type: () -> Optional[Enum]
        """Default Enum value. Set default value to `__default__` attribute
        of your enum class or override this method if you need another
        default value.
        Usage:
            IntegerField(choices=my_enum.choices(), default=my_enum.default(), ...
        :return Default value, if set.
        """
        if cls.__default__ is not None:
            return cast(Enum, cls(cls.__default__))
        return None

    @classmethod
    def field(cls, **kwargs):
        # type: (Any) -> EnumField
        """A shortcut for field declaration
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
    def get(
        cls,
        name_or_numeric,  # type: Union[str, int, T]
        default=None,  # type: Optional[Default]
    ):
        # type: (...) -> Union[Enum, Optional[Default]]
        """Get Enum.Value object matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :param default: The default to return if the value passed is not
            a valid enum value
        """
        if isinstance(name_or_numeric, cls):
            return name_or_numeric

        if isinstance(name_or_numeric, int):
            try:
                return cls(name_or_numeric)
            except ValueError:
                pass
        elif isinstance(name_or_numeric, str):
            try:
                return cls[name_or_numeric]
            except KeyError:
                pass

        return default

    @classmethod
    def get_name(cls, name_or_numeric):
        # type: (Union[str, int, T]) -> Optional[str]
        """Get Enum.Value name matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :return: The name or None if not found
        """
        value = cls.get(name_or_numeric)
        if value is not None:
            return value.name
        return None

    @classmethod
    def get_label(cls, name_or_numeric):
        # type: (Union[str, int, Enum]) -> Optional[str]
        """Get Enum.Value label matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :return: The label or None if not found
        """
        value = cls.get(name_or_numeric)
        if value is not None:
            return value.label
        return None

    @classmethod
    def is_valid_transition(cls, from_value, to_value):
        # type: (Union[int, Enum], Union[int, Enum]) -> bool
        """Will check if to_value is a valid transition from from_value.
        Returns true if it is a valid transition.

        :param from_value: Start transition point
        :param to_value: End transition point
        :return: Success flag
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
        # type: (Union[int, T]) -> Sequence[int]
        """Returns all values the to_value can make a transition from.
        :param to_value End transition point
        """
        if isinstance(to_value, cls):
            to_value = to_value.value

        return cls.__transitions__.get(to_value, [])
