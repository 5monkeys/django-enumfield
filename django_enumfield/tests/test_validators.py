import unittest

from django.db import models

from django_enumfield.exceptions import InvalidStatusOperationError
from django_enumfield.tests.models import BeerStyle, Person, PersonStatus
from django_enumfield.validators import validate_available_choice


class ValidatorTest(unittest.TestCase):
    def test_validate_available_choice_1(self):
        """Test passing a value non convertible to an int raises an
        InvalidStatusOperationError
        """
        self.assertRaises(
            InvalidStatusOperationError,
            validate_available_choice,
            *(BeerStyle, "Not an int")
        )

    def test_validate_available_choice_2(self):
        """Test passing an int as a string validation"""
        self.assertRaises(
            InvalidStatusOperationError,
            validate_available_choice,
            BeerStyle,
            str(BeerStyle.LAGER.value),
        )

    def test_validate_available_choice_3(self):
        """Test passing an int validation"""
        self.assertIsNone(validate_available_choice(BeerStyle, BeerStyle.LAGER))

    def test_validate_by_setting(self):
        person = Person()
        with self.assertRaises(InvalidStatusOperationError):
            person.status = PersonStatus.UNBORN

        with self.assertRaises(InvalidStatusOperationError):
            person.status = models.NOT_PROVIDED
