from enum import Enum as NativeEnum

from django import forms


class EnumChoiceField(forms.TypedChoiceField):
    def __init__(self, enum, **kwargs):
        kwargs.setdefault(
            "choices", enum.choices(blank=not kwargs.get("required", True))
        )
        kwargs.setdefault("coerce", int)
        super(EnumChoiceField, self).__init__(**kwargs)
        self.enum = enum

    def prepare_value(self, value):
        if isinstance(value, NativeEnum):
            return value.value
        return value

    def clean(self, value):
        value = super(EnumChoiceField, self).clean(value)
        if value == self.empty_value:
            return value
        return self.enum(value)
