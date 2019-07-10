from django.test import TestCase

from django_enumfield.contrib.drf import EnumField, NamedEnumField
from django_enumfield.tests.models import BeerState, LampState


class DRFTestCase(TestCase):
    def test_enum_field(self):
        field = EnumField(BeerState)
        self.assertEqual(field.to_internal_value("0"), BeerState.FIZZY)
        self.assertEqual(
            field.to_internal_value(BeerState.EMPTY.value), BeerState.EMPTY
        )
        self.assertEqual(
            field.to_representation(BeerState.FIZZY), BeerState.FIZZY.value
        )

    def test_named_enum_field(self):
        field = NamedEnumField(LampState)
        self.assertEqual(field.to_internal_value("1"), LampState.ON)
        self.assertEqual(field.to_representation(LampState.OFF), "OFF")
