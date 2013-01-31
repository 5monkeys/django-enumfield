from django.utils.translation import gettext as _
from django_enumfield.exceptions import InvalidStatusOperationError


def validate_valid_transition(enum, from_value, to_value):
    """
    Validate that to_value is a valid choice and that to_value is a valid transition from from_value.
    """
    validate_available_choice(enum, to_value)
    if hasattr(enum, '_transitions') and not enum.is_valid_transition(from_value, to_value):
        message = _('%(enum)s can not go from "%(from)s" to "%(to)s"' % {'enum': enum.__name__,
                                                                         'from': enum.name(from_value),
                                                                         'to': enum.name(to_value) or to_value})
        raise InvalidStatusOperationError(message)


def validate_available_choice(enum, to_value):
    """
    Validate that to_value is defined as a value in enum.
    """
    if to_value is not None and not to_value in dict(enum.choices()).keys():
        raise InvalidStatusOperationError(_(u'Select a valid choice. %(value)s is not one of the available choices.') % {'value': to_value})
