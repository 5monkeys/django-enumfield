from __future__ import absolute_import

from enum import Enum

from django.utils import six
from django.utils.translation import gettext as _

from django_enumfield.exceptions import InvalidStatusOperationError


def validate_valid_transition(enum, from_value, to_value):
    """
    Validate that to_value is a valid choice and that to_value is
    a valid transition from from_value.
    """
    validate_available_choice(enum, to_value)
    if isinstance(to_value, Enum):
        t_value = to_value.value
    else:
        t_value = to_value

    if isinstance(from_value, Enum):
        f_value = from_value.value
    else:
        f_value = from_value

    if not enum.is_valid_transition(f_value, t_value):
        message = _(
            six.text_type('{enum} can not go from "{from_value}" to "{to_value}"')
        )
        raise InvalidStatusOperationError(
            message.format(
                enum=enum.__name__,
                from_value=getattr(from_value, "name", None) or from_value,
                to_value=getattr(to_value, "name", None) or to_value,
            )
        )


def validate_available_choice(enum, to_value):
    """
    Validate that to_value is defined as a value in enum.
    """
    if to_value is None:
        return

    enum.get(to_value)
