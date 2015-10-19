from enum import Enum

from django.db import models
from django.utils.functional import curry
from django.utils.encoding import force_text
from django import forms

from django_enumfield import validators


class EnumField(models.Field):
    """ EnumField is a convenience field to automatically handle validation of transitions
        between Enum values and set field choices from the enum.
        EnumField(MyEnum, default=MyEnum.INITIAL)
    """
    default_error_messages = models.IntegerField.default_error_messages

    def __init__(self, enum, *args, **kwargs):
        kwargs['choices'] = enum.choices()
        if 'default' not in kwargs:
            kwargs['default'] = enum.default()
        self.enum = enum
        super(EnumField, self).__init__(self, *args, **kwargs)

    def get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

    def get_internal_type(self):
        return "IntegerField"

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(EnumField, self).contribute_to_class(cls, name)
        if self.choices:
            setattr(cls, 'get_%s_display' % self.name,
                    curry(self._get_FIELD_display))
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

    def from_db_value(self, value, expression, connection, context):
        if value is not None:
            return self.enum.get(value)

        return value

    def to_python(self, value):
        if value is not None:
            return self.enum.get(value)

    def _setup_validation(self, sender, **kwargs):
        """
        User a customer setter for the field to validate new value against the old one.
        The current value is set as '_enum_[att_name]' on the model instance.
        """
        att_name = self.get_attname()
        private_att_name = '_enum_%s' % att_name
        enum = self.enum

        def set_enum(self, new_value):
            if hasattr(self, private_att_name):
                # Fetch previous value from private enum attribute.
                old_value = getattr(self, private_att_name)
            else:
                # First setattr no previous value on instance.
                old_value = new_value
            # Update private enum attribute with new value
            setattr(self, private_att_name, new_value)
            # Run validation for new value.
            validators.validate_valid_transition(enum, old_value, new_value)

        def get_enum(self):
            return getattr(self, private_att_name)

        def delete_enum(self):
            return setattr(self, private_att_name, None)

        if not sender._meta.abstract:
            setattr(sender, att_name, property(get_enum, set_enum, delete_enum))

    def validate(self, value, model_instance):
        super(EnumField, self).validate(value, model_instance)
        validators.validate_valid_transition(self.enum, self.value_from_object(model_instance), value)

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Select,
                    'form_class': forms.TypedChoiceField,
                    'coerce': int,
                    'choices': self.enum.choices(blank=self.blank)}
        defaults.update(kwargs)
        return super(EnumField, self).formfield(**defaults)

    def south_field_triple(self):
        """Returns a suitable description of this field for South."""
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector

        field_class = "django.db.models.fields.IntegerField"
        args, kwargs = introspector(self)
        # That's our definition!
        return field_class, args, kwargs

    def deconstruct(self):
        name, path, args, kwargs = super(EnumField, self).deconstruct()
        kwargs['enum'] = self.enum
        del kwargs['verbose_name']
        return name, path, args, kwargs
