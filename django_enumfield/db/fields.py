from enum import Enum
from functools import partial
from typing import Any, Callable  # noqa: F401

import six
from django import forms
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext

from django_enumfield.exceptions import InvalidStatusOperationError
from django_enumfield.forms.fields import EnumChoiceField

from .. import validators

try:
    from functools import partialmethod as _partialmethod

    def partialishmethod(method):
        return _partialmethod(method)


except ImportError:  # pragma: no cover
    from django.utils.functional import curry

    def partialishmethod(method):
        return curry(method)


class EnumField(models.IntegerField):
    """ EnumField is a convenience field to automatically handle validation of transitions
        between Enum values and set field choices from the enum.
        EnumField(MyEnum, default=MyEnum.INITIAL)
    """

    default_error_messages = models.IntegerField.default_error_messages  # type: ignore

    def __init__(self, enum, *args, **kwargs):
        kwargs.setdefault("choices", enum.choices())
        if enum.default() is not None:
            kwargs.setdefault("default", enum.default())
        self.enum = enum
        super(EnumField, self).__init__(*args, **kwargs)

    def get_default(self):
        if self.has_default() and callable(self.default):
            return self.default()
        return self.default

    def get_internal_type(self):
        return "IntegerField"

    def contribute_to_class(
        self, cls, name, private_only=False, virtual_only=models.NOT_PROVIDED
    ):
        super(EnumField, self).contribute_to_class(cls, name)
        if self.choices:
            setattr(
                cls,
                "get_%s_display" % self.name,
                partialishmethod(self._get_FIELD_display),
            )
        models.signals.class_prepared.connect(self._setup_validation, sender=cls)

    def _get_FIELD_display(self, cls):
        value = getattr(cls, self.attname)
        return force_text(value.label, strings_only=True)

    def get_prep_value(self, value):
        value = super(EnumField, self).get_prep_value(value)
        if value is None:
            return value

        if isinstance(value, Enum):
            return value.value
        return int(value)

    def from_db_value(self, value, *_):
        if value is not None:
            return self.enum.get(value)

        return value

    def to_python(self, value):
        if value is not None:
            if isinstance(value, six.text_type) and value.isdigit():
                value = int(value)
            return self.enum.get(value)

    def _setup_validation(self, sender, **kwargs):
        """
        User a customer setter for the field to validate new value against the old one.
        The current value is set as '_enum_[att_name]' on the model instance.
        """
        att_name = self.get_attname()
        private_att_name = "_enum_%s" % att_name
        enum = self.enum

        def set_enum(self, new_value):
            if new_value is models.NOT_PROVIDED:
                new_value = None
            if hasattr(self, private_att_name):
                # Fetch previous value from private enum attribute.
                old_value = getattr(self, private_att_name)
            else:
                # First setattr no previous value on instance.
                old_value = new_value
            # Update private enum attribute with new value
            if new_value is not None and not isinstance(new_value, enum):
                if isinstance(new_value, Enum):
                    raise TypeError(
                        "Invalid Enum class passed. Passed {}, expected {}".format(
                            new_value.__class__.__name__, enum.__name__
                        )
                    )
                try:
                    new_value = enum(new_value)
                except ValueError:
                    raise InvalidStatusOperationError(
                        ugettext(
                            six.text_type(
                                "{value!r} is not one of the available choices "
                                "for enum {enum}."
                            )
                        ).format(value=new_value, enum=enum)
                    )
            setattr(self, private_att_name, new_value)
            self.__dict__[att_name] = new_value
            # Run validation for new value.
            validators.validate_valid_transition(enum, old_value, new_value)

        def get_enum(self):
            return getattr(self, private_att_name)

        def delete_enum(self):
            self.__dict__[att_name] = None
            return setattr(self, private_att_name, None)

        if not sender._meta.abstract:
            setattr(sender, att_name, property(get_enum, set_enum, delete_enum))

    def validate(self, value, model_instance):
        super(EnumField, self).validate(value, model_instance)
        validators.validate_valid_transition(
            self.enum, self.value_from_object(model_instance), value
        )

    def formfield(self, **kwargs):
        enum_form_class = partial(EnumChoiceField, enum=self.enum)
        defaults = {
            "widget": forms.Select,
            "form_class": enum_form_class,
            "choices_form_class": enum_form_class,
            "choices": self.enum.choices(blank=self.blank),
        }
        defaults.update(kwargs)
        return super(EnumField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(EnumField, self).deconstruct()
        kwargs["enum"] = self.enum
        if "choices" in kwargs:
            del kwargs["choices"]
        if "verbose_name" in kwargs:
            del kwargs["verbose_name"]
        if "default" in kwargs and isinstance(kwargs["default"], self.enum):
            # The enum value cannot be deconstructed properly
            # for migrations (on django <= 1.8).
            # So we send the int value instead.
            kwargs["default"] = kwargs["default"].value

        return name, path, args, kwargs
