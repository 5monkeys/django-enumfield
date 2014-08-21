import unittest
from django_enumfield.tests.models import BeerStyle
from django_enumfield.validators import validate_available_choice
from django_enumfield.exceptions import InvalidStatusOperationError


class ValidatorTest(unittest.TestCase):
    def test_validate_available_choice_1(self):
        """Test passing a value non convertable to an int raises an
        InvalidStatusOperationError
        """
        self.assertRaises(
            InvalidStatusOperationError,
            validate_available_choice,
            *(BeerStyle, 'Not an int')
        )

    def test_validate_available_choice_2(self):
        """Test passing an int as a string validation
        """
        self.assertIsNone(
            validate_available_choice(BeerStyle, '%s' % BeerStyle.LAGER)
        )

    def test_validate_available_choice_3(self):
        """Test passing an int validation
        """
        self.assertIsNone(
            validate_available_choice(BeerStyle, BeerStyle.LAGER)
        )
