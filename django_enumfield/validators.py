from __future__ import absolute_import

from django.utils.translation import gettext as _

from django_enumfield.exceptions import InvalidStatusOperationError


def validate_valid_transition(enum, from_value, to_value):
    """
    Validate that to_value is a valid choice and that to_value is
    a valid transition from from_value.
    """
    validate_available_choice(enum, to_value)
    if not enum.is_valid_transition(from_value, to_value):
        message = _('{enum} can not go from "{from_value}" to "{to_value}"')
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
    Pass by name is not supported.
    """
    if to_value is None:
        return

    try:
        enum(to_value)
    except ValueError:
        raise InvalidStatusOperationError(
            _(
                "{value!r} is not one of the available choices " "for enum {enum}."
            ).format(value=to_value, enum=enum)
        )
