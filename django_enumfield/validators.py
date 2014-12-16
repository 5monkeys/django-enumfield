from django.utils.translation import gettext as _
from django.utils import six

from django_enumfield.exceptions import InvalidStatusOperationError


def validate_valid_transition(enum, from_value, to_value):
    """
    Validate that to_value is a valid choice and that to_value is a valid transition from from_value.
    """
    validate_available_choice(enum, to_value)
    if hasattr(enum, '_transitions') and not enum.is_valid_transition(from_value, to_value):
        message = _(six.text_type('{enum} can not go from "{from_value}" to "{to_value}"'))
        raise InvalidStatusOperationError(message.format(
            enum=enum.__name__,
            from_value=enum.name(from_value),
            to_value=enum.name(to_value) or to_value
        ))


def validate_available_choice(enum, to_value):
    """
    Validate that to_value is defined as a value in enum.
    """
    if to_value is None:
        return

    if type(to_value) is not int:
        try:
            to_value = int(to_value)
        except ValueError:
            message_str = "'{value}' cannot be converted to int"
            message = _(six.text_type(message_str))
            raise InvalidStatusOperationError(message.format(value=to_value))

    if to_value not in list(dict(enum.choices()).keys()):
        message = _(six.text_type('Select a valid choice. {value} is not one of the available choices.'))
        raise InvalidStatusOperationError(message.format(value=to_value))
