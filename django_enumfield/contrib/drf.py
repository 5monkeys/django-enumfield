from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    default_error_messages = {"invalid_choice": _('"{input}" is not a valid choice.')}

    def __init__(self, enum, **kwargs):
        self.enum = enum
        choices = (
            (self.get_choice_value(enum_value), enum_value.label)
            for _, enum_value in enum.choices()
        )
        super(EnumField, self).__init__(choices, **kwargs)

    def get_choice_value(self, enum_value):
        return enum_value.value

    def to_internal_value(self, data):
        if isinstance(data, str) and data.isdigit():
            data = int(data)

        try:
            value = self.enum.get(data).value
        except AttributeError:  # .get() returned None
            if not self.required:
                raise serializers.SkipField()
            self.fail("invalid_choice", input=data)

        return value

    def to_representation(self, value):
        enum_value = self.enum.get(value)
        if enum_value is not None:
            return self.get_choice_value(enum_value)


class NamedEnumField(EnumField):
    def get_choice_value(self, enum_value):
        return enum_value.name

    class Meta:
        swagger_schema_fields = {"type": "string"}
