from django.db import models
from django import forms
from django_enumfield import validators


class EnumField(models.IntegerField):
    """ EnumField is a convenience field to automatically handle validation of transitions
        between Enum values and set field choices from the enum.
        EnumField(MyEnum, default=MyEnum.INITIAL)
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, enum, *args, **kwargs):
        default = kwargs.get('default')
        db_index = kwargs.get('db_index')
        kwargs['choices'] = enum.choices()
        if not default:
            kwargs['default'] = enum.default()
        if not db_index:
            kwargs['db_index'] = True
        self.enum = enum
        models.IntegerField.__init__(self, *args, **kwargs)

    def contribute_to_class(self, cls, name):
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
                    'choices': self.enum.choices()}
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
