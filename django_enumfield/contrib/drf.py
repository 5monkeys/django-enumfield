from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    default_error_messages = {
        "invalid_choice": _('"{input}" is not a valid choice.')
    }

    def __init__(self, enum, **kwargs):
        self.enum = enum
        self.name_as_value = kwargs.pop("name_as_value", False)
        choices = (
            (
                val.value if not self.name_as_value else enum.name(val.value),
                val.label
            )
            for _, val in enum.choices()
        )
        super().__init__(choices, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, str) and data.isdigit():
            data = int(data)

        try:
            value = self.enum.get(data).value
        except AttributeError:
            if not self.required:
                raise serializers.SkipField()
            self.fail("invalid_choice", input=data)

        return value

    def to_representation(self, value):
        enum = self.enum.get(value)
        if enum:
            return enum.value if not self.name_as_value else enum.name
