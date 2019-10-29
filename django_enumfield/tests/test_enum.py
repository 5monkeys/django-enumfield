from contextlib import contextmanager
from os.path import abspath, dirname, exists, join

import six
from django import forms
from django.core.management import call_command
from django.db import IntegrityError, connection
from django.db.backends.sqlite3.base import DatabaseWrapper
from django.db.models.fields import NOT_PROVIDED
from django.test import TestCase
from django.test.client import RequestFactory

from django_enumfield.db.fields import EnumField
from django_enumfield.enum import BlankEnum, Enum
from django_enumfield.exceptions import InvalidStatusOperationError
from django_enumfield.forms.fields import EnumChoiceField
from django_enumfield.tests.models import (
    Beer,
    BeerState,
    BeerStyle,
    LabelBeer,
    Lamp,
    LampState,
    Person,
    PersonStatus,
    PersonStatusDefault,
)


def _mock_disable_constraint_checking(self):
    self.cursor().execute("PRAGMA foreign_keys = OFF")
    return True


def _mock_enable_constraint_checking(self):
    self.needs_rollback, needs_rollback = False, self.needs_rollback
    try:
        self.cursor().execute("PRAGMA foreign_keys = ON")
    finally:
        self.needs_rollback = needs_rollback


@contextmanager
def patch_sqlite_connection():
    if connection.vendor != "sqlite":  # pragma: no cover
        yield
        return

    # Patch sqlite3 connection to drop foreign key constraints before
    # running migration
    old_enable = DatabaseWrapper.enable_constraint_checking
    old_disable = DatabaseWrapper.disable_constraint_checking
    DatabaseWrapper.enable_constraint_checking = _mock_enable_constraint_checking
    DatabaseWrapper.disable_constraint_checking = _mock_disable_constraint_checking

    try:
        yield
    finally:
        DatabaseWrapper.enable_constraint_checking = old_enable
        DatabaseWrapper.disable_constraint_checking = old_disable


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ("status",)


class EnumFieldTest(TestCase):
    def test_enum_field_init(self):
        for enum, default in {
            PersonStatus: NOT_PROVIDED,
            PersonStatusDefault: PersonStatusDefault.UNBORN,
        }.items():
            field = EnumField(enum)
            self.assertEqual(field.default, default)
            self.assertEqual(len(enum.choices()), len(field.choices))
            field = EnumField(enum, default=enum.ALIVE)
            self.assertEqual(field.default, enum.ALIVE)
            field = EnumField(enum, default=None)
            self.assertEqual(field.default, None)

    def test_enum_field_save(self):
        # Test model with EnumField WITHOUT __transitions__

        lamp = Lamp.objects.create()
        self.assertEqual(lamp.state, LampState.OFF)
        lamp.state = LampState.ON
        lamp.save()
        self.assertEqual(lamp.state, LampState.ON)
        self.assertEqual(lamp.state, 1)

        self.assertRaises(InvalidStatusOperationError, setattr, lamp, "state", 99)

        # Test model with EnumField WITH __transitions__
        person = Person.objects.create()
        pk = person.pk
        self.assertEqual(person.status, PersonStatus.ALIVE)
        person.status = PersonStatus.DEAD
        person.save()
        self.assertTrue(isinstance(person.status, PersonStatus))
        self.assertEqual(person.status, PersonStatus.DEAD)

        person = Person.objects.get(pk=pk)
        self.assertEqual(person.status, PersonStatus.DEAD)
        self.assertTrue(isinstance(person.status, int))
        self.assertTrue(isinstance(person.status, PersonStatus))

        self.assertRaises(InvalidStatusOperationError, setattr, person, "status", 99)

        person = Person.objects.create(status=PersonStatus.ALIVE)
        self.assertRaises(
            InvalidStatusOperationError, setattr, person, "status", PersonStatus.UNBORN
        )

        person.status = PersonStatus.DEAD
        self.assertEqual(person.save(), "Person.save")

        with self.assertRaises(InvalidStatusOperationError):
            person.status = PersonStatus.VOID
            person.save()

        self.assertTrue(Person.objects.filter(status=PersonStatus.DEAD).exists())
        beer = Beer.objects.create()
        beer.style = BeerStyle.LAGER
        self.assertEqual(beer.state, BeerState.FIZZY)
        beer.save()

    def test_enum_field_refresh_from_db(self):
        lamp = Lamp.objects.create(state=LampState.OFF)
        lamp2 = Lamp.objects.get(pk=lamp.id)

        lamp.state = LampState.ON
        lamp.save()

        self.assertEqual(lamp.state, LampState.ON)
        self.assertEqual(lamp2.state, LampState.OFF)

        lamp2.refresh_from_db()
        self.assertEqual(lamp2.state, LampState.ON)

    def test_magic_model_properties(self):
        beer = Beer.objects.create(style=BeerStyle.WEISSBIER)
        self.assertEqual(getattr(beer, "get_style_display")(), "WEISSBIER")

    def test_enum_field_del(self):
        lamp = Lamp.objects.create()
        del lamp.state
        self.assertEqual(lamp.state, None)
        self.assertRaises(IntegrityError, lamp.save)

    def test_enum_field_del_save(self):
        beer = Beer.objects.create()
        beer.style = BeerStyle.STOUT
        beer.state = None
        beer.save()
        self.assertEqual(beer.state, None)
        self.assertEqual(beer.style, BeerStyle.STOUT)

    def test_enum_field_modelform_create(self):
        request_factory = RequestFactory()
        request = request_factory.post("", data={"status": "2"})
        form = PersonForm(request.POST)
        self.assertTrue(isinstance(form.fields["status"], forms.TypedChoiceField))
        self.assertTrue(form.is_valid())
        person = form.save()
        self.assertTrue(person.status, PersonStatus.DEAD)

        request = request_factory.post("", data={"status": "99"})
        form = PersonForm(request.POST, instance=person)
        self.assertFalse(form.is_valid())

    def test_enum_field_modelform(self):
        person = Person.objects.create()

        request_factory = RequestFactory()
        request = request_factory.post("", data={"status": "2"})
        form = PersonForm(request.POST, instance=person)
        self.assertTrue(isinstance(form.fields["status"], forms.TypedChoiceField))
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(person.status, PersonStatus.DEAD)

        request = request_factory.post("", data={"status": "99"})
        form = PersonForm(request.POST, instance=person)
        self.assertFalse(form.is_valid())

    def test_enum_field_modelform_initial(self):
        person = Person.objects.create()
        form = PersonForm(instance=person)
        self.assertEqual(form.fields["status"].initial, PersonStatus.ALIVE.value)
        self.assertIn(
            u'<option value="{}" selected'.format(PersonStatus.ALIVE.value),
            six.text_type(form["status"]),
        )

    def test_enum_field_nullable_field(self):
        class BeerForm(forms.ModelForm):
            class Meta:
                model = Beer
                fields = ("style", "state")

        form = BeerForm()

        self.assertEqual(len(form.fields["style"].choices), 3)
        self.assertEqual(form.fields["style"].choices[0][1].label, "LAGER")
        self.assertEqual(form.fields["style"].choices[1][1].label, "STOUT")
        self.assertEqual(form.fields["style"].choices[2][1].label, "WEISSBIER")

        self.assertEqual(len(form.fields["state"].choices), 4)
        self.assertEqual(form.fields["state"].choices[0][1].label, "")
        self.assertEqual(form.fields["state"].choices[1][1].label, "FIZZY")
        self.assertEqual(form.fields["state"].choices[2][1].label, "STALE")
        self.assertEqual(form.fields["state"].choices[3][1].label, "EMPTY")

    def test_migration(self):
        app_dir = dirname(abspath(__file__))
        self.assertTrue(exists(join(app_dir, "models.py")))

        migrations_dir = join(app_dir, "migrations")
        self.assertTrue(not exists(migrations_dir))

        call_command("makemigrations", "tests")
        with patch_sqlite_connection():
            call_command("sqlmigrate", "tests", "0001")

    def test_enum_form_field(self):
        class CustomPersonForm(forms.Form):
            status = EnumChoiceField(PersonStatus)

        form = CustomPersonForm(initial={"status": PersonStatus.DEAD})
        self.assertEqual(form["status"].initial, PersonStatus.DEAD.value)
        self.assertIn(
            u'<option value="{}" selected'.format(PersonStatus.DEAD.value),
            six.text_type(form["status"]),
        )
        self.assertEqual(form.fields["status"].choices, PersonStatus.choices())

        # Test validation

        form = CustomPersonForm(
            data={"status": six.text_type(PersonStatus.ALIVE.value)},
            initial={"status": PersonStatus.DEAD.value},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["status"], PersonStatus.ALIVE)

    def test_enum_form_field_not_required(self):
        class CustomPersonForm(forms.Form):
            status = EnumChoiceField(PersonStatus, required=False)

        form = CustomPersonForm(
            data={"status": None}, initial={"status": PersonStatus.DEAD.value}
        )
        self.assertEqual(
            form.fields["status"].choices, PersonStatus.choices(blank=True)
        )
        self.assertIn(u'<option value="" selected', six.text_type(form["status"]))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["status"], six.text_type())


class EnumTest(TestCase):
    def test_label(self):
        self.assertEqual(PersonStatus.ALIVE.label, six.text_type("ALIVE"))
        self.assertEqual(LabelBeer.STELLA.label, six.text_type("Stella Artois"))
        self.assertEqual(
            LabelBeer.label(LabelBeer.STELLA), six.text_type("Stella Artois")
        )

        # Same as when coercing to string
        self.assertEqual(six.text_type(PersonStatus.ALIVE), six.text_type("ALIVE"))
        self.assertEqual(
            six.text_type(LabelBeer.STELLA), six.text_type("Stella Artois")
        )

    def test_name(self):
        self.assertEqual(PersonStatus.ALIVE.name, six.text_type("ALIVE"))
        self.assertEqual(LabelBeer.STELLA.name, six.text_type("STELLA"))

        # Check that the old classmethod still works. Kept for backward compatibility.
        self.assertEqual(
            LabelBeer.name(LabelBeer.STELLA.value), six.text_type("STELLA")
        )
        self.assertEqual(PersonStatus.name("ALIVE"), six.text_type("ALIVE"))
        self.assertEqual(PersonStatus.name(PersonStatus.ALIVE), six.text_type("ALIVE"))

    def test_get(self):
        self.assertTrue(isinstance(PersonStatus.get(PersonStatus.ALIVE), Enum))
        self.assertTrue(isinstance(PersonStatus.get(six.text_type("ALIVE")), Enum))
        self.assertEqual(
            PersonStatus.get(PersonStatus.ALIVE),
            PersonStatus.get(six.text_type("ALIVE")),
        )

        # Returns `default` if not found
        self.assertEqual(PersonStatus.get("ALIVEISH", "?"), "?")
        self.assertEqual(PersonStatus.get(99, "??"), "??")

    def test_get_name(self):
        self.assertEqual(PersonStatus.get_name(PersonStatus.ALIVE), "ALIVE")
        self.assertEqual(PersonStatus.get_name(PersonStatus.ALIVE.value), "ALIVE")
        self.assertEqual(PersonStatus.get_name(PersonStatus.ALIVE.name), "ALIVE")
        self.assertIsNone(PersonStatus.get_name(89))

    def test_get_label(self):
        self.assertEqual(LabelBeer.get_label(LabelBeer.STELLA), "Stella Artois")
        self.assertEqual(LabelBeer.get_label(LabelBeer.STELLA.value), "Stella Artois")
        self.assertEqual(LabelBeer.get_label(LabelBeer.STELLA.name), "Stella Artois")
        self.assertIsNone(LabelBeer.get_label(89))

    def test_choices(self):
        self.assertEqual(len(PersonStatus.choices()), len(PersonStatus))
        for value, member in PersonStatus.choices():
            self.assertTrue(isinstance(value, int))
            self.assertTrue(isinstance(member, PersonStatus))
            self.assertTrue(PersonStatus.get(value) == member)
        blank = PersonStatus.choices(blank=True)[0]
        self.assertEqual(blank, (BlankEnum.BLANK.value, BlankEnum.BLANK))

    def test_items(self):
        self.assertEqual(len(PersonStatus.items()), len(PersonStatus))
        for name, value in PersonStatus.items():
            self.assertTrue(isinstance(value, int))
            self.assertTrue(isinstance(name, six.string_types))
            self.assertEqual(PersonStatus.get(value), PersonStatus.get(name))

    def test_default(self):
        for enum, default in {
            PersonStatus: None,
            PersonStatusDefault: PersonStatusDefault.UNBORN,
        }.items():
            self.assertEqual(enum.default(), default)

    def test_field(self):
        self.assertTrue(isinstance(PersonStatus.field(), EnumField))

    def test_equal(self):
        self.assertTrue(PersonStatus.ALIVE == PersonStatus.ALIVE)
        self.assertFalse(PersonStatus.ALIVE == PersonStatus.DEAD)
        self.assertEqual(
            PersonStatus.get(PersonStatus.ALIVE), PersonStatus.get(PersonStatus.ALIVE)
        )

    def test_labels(self):
        self.assertEqual(LabelBeer.JUPILER.name, LabelBeer.JUPILER.label)
        self.assertNotEqual(LabelBeer.STELLA.name, LabelBeer.STELLA.label)
        self.assertTrue(isinstance(LabelBeer.STELLA.label, six.string_types))
        self.assertEqual(LabelBeer.STELLA.label, six.text_type("Stella Artois"))

        # Check that the old classmethod still works. Kept for backward compatibility.
        self.assertEqual(
            LabelBeer.label(LabelBeer.STELLA.value), six.text_type("Stella Artois")
        )
        self.assertEqual(LabelBeer.label("STELLA"), six.text_type("Stella Artois"))

    def test_hash(self):
        self.assertTrue({LabelBeer.JUPILER: True}[LabelBeer.JUPILER])

    def test_comparison(self):
        self.assertGreater(PersonStatus.ALIVE, PersonStatus.UNBORN.value)
        self.assertLess(PersonStatus.REANIMATED, PersonStatus.VOID)
        self.assertGreater(PersonStatus.ALIVE, PersonStatus.UNBORN.value)

    def test_values(self):
        self.assertEqual(
            PersonStatus.values,
            {
                PersonStatus.UNBORN.value: PersonStatus.UNBORN,
                PersonStatus.ALIVE.value: PersonStatus.ALIVE,
                PersonStatus.DEAD.value: PersonStatus.DEAD,
                PersonStatus.REANIMATED.value: PersonStatus.REANIMATED,
                PersonStatus.VOID.value: PersonStatus.VOID,
            },
        )
