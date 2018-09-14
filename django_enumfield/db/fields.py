import django
from django.db import models
from django import forms

from django_enumfield import validators


class EnumField(models.IntegerField):
    """ EnumField is a convenience field to automatically handle validation of transitions
        between Enum values and set field choices from the enum.
        EnumField(MyEnum, default=MyEnum.INITIAL)
    """

    def __init__(self, enum, *args, **kwargs):
        kwargs['choices'] = enum.choices()
        if 'default' not in kwargs:
            kwargs['default'] = enum.default()
        self.enum = enum
        models.IntegerField.__init__(self, *args, **kwargs)

    def contribute_to_class(
        self, cls, name, private_only=False, virtual_only=models.NOT_PROVIDED
    ):
        super(EnumField, self).contribute_to_class(cls, name)
        models.signals.class_prepared.connect(self._setup_validation, sender=cls)

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
        validators.validate_valid_transition(self.enum, self.value_from_object(model_instance), value)

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Select,
                    'form_class': forms.TypedChoiceField,
                    'coerce': int,
                    'choices': self.enum.choices(blank=self.blank)}
        defaults.update(kwargs)
        return super(EnumField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(EnumField, self).deconstruct()
        if django.VERSION >= (1, 9):
            kwargs['enum'] = self.enum
        else:
            path = "django.db.models.fields.IntegerField"
        if 'choices' in kwargs:
            del kwargs['choices']
        return name, path, args, kwargs
