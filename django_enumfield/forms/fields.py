from enum import Enum as NativeEnum

from django import forms


class EnumChoiceField(forms.TypedChoiceField):
    def __init__(self, enum=None, **kwargs):
        if enum is not None:
            kwargs.setdefault("choices", enum.choices())
        kwargs.setdefault("coerce", int)
        super(EnumChoiceField, self).__init__(**kwargs)
        self.enum = enum

    def prepare_value(self, value):
        if isinstance(value, NativeEnum):
            return value.value
        return value
