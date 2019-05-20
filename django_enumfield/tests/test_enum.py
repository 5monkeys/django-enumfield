from os.path import abspath, dirname, join, exists

from django.core.management import call_command
from django.test.client import RequestFactory
from django.db import IntegrityError
from django.db.models.fields import NOT_PROVIDED
from django.forms import ModelForm, TypedChoiceField
from django.test import TestCase
from django.utils import six

from django_enumfield.db.fields import EnumField
from django_enumfield.enum import Enum, BlankEnum
from django_enumfield.exceptions import InvalidStatusOperationError
from django_enumfield.tests.models import Person, PersonStatus, Lamp, \
    LampState, Beer, BeerStyle, BeerState, LabelBeer, PersonStatusDefault


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

        self.assertRaises(InvalidStatusOperationError, setattr, lamp, 'state', 99)

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

        self.assertRaises(InvalidStatusOperationError, setattr, person, 'status', 99)

        person = Person.objects.create(status=PersonStatus.ALIVE)
        self.assertRaises(InvalidStatusOperationError, setattr, person, 'status', PersonStatus.UNBORN)

        person.status = PersonStatus.DEAD
        self.assertEqual(person.save(), 'Person.save')

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
        self.assertEqual(getattr(beer, 'get_style_display')(), 'WEISSBIER')

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
        class PersonForm(ModelForm):
            class Meta:
                model = Person
                fields = ('status',)

        request_factory = RequestFactory()
        request = request_factory.post('', data={'status': '2'})
        form = PersonForm(request.POST)
        self.assertTrue(isinstance(form.fields['status'], TypedChoiceField))
        self.assertTrue(form.is_valid())
        person = form.save()
        self.assertTrue(person.status, PersonStatus.DEAD)

        request = request_factory.post('', data={'status': '99'})
        form = PersonForm(request.POST, instance=person)
        self.assertFalse(form.is_valid())

    def test_enum_field_modelform(self):
        person = Person.objects.create()

        class PersonForm(ModelForm):
            class Meta:
                model = Person
                fields = ('status',)

        request_factory = RequestFactory()
        request = request_factory.post('', data={'status': '2'})
        form = PersonForm(request.POST, instance=person)
        self.assertTrue(isinstance(form.fields['status'], TypedChoiceField))
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(person.status, PersonStatus.DEAD)

        request = request_factory.post('', data={'status': '99'})
        form = PersonForm(request.POST, instance=person)
        self.assertFalse(form.is_valid())

    def test_enum_field_nullable_field(self):
        class BeerForm(ModelForm):
            class Meta:
                model = Beer
                fields = ('style', 'state')

        form = BeerForm()

        self.assertEqual(len(form.fields['style'].choices), 3)
        self.assertEqual(form.fields['style'].choices[0][1].label, 'LAGER')
        self.assertEqual(form.fields['style'].choices[1][1].label, 'STOUT')
        self.assertEqual(form.fields['style'].choices[2][1].label, 'WEISSBIER')

        self.assertEqual(len(form.fields['state'].choices), 4)
        self.assertEqual(form.fields['state'].choices[0][1].label, '')
        self.assertEqual(form.fields['state'].choices[1][1].label, 'FIZZY')
        self.assertEqual(form.fields['state'].choices[2][1].label, 'STALE')
        self.assertEqual(form.fields['state'].choices[3][1].label, 'EMPTY')

    def test_migration(self):
        app_dir = dirname(abspath(__file__))
        self.assertTrue(exists(join(app_dir, 'models.py')))

        migrations_dir = join(app_dir, 'migrations')
        self.assertTrue(not exists(migrations_dir))

        call_command('makemigrations', 'tests')
        call_command('sqlmigrate', 'tests', '0001')


class EnumTest(TestCase):
    def test_label(self):
        self.assertEqual(PersonStatus.ALIVE.label, six.text_type('ALIVE'))
        self.assertEqual(LabelBeer.STELLA.label,
                         six.text_type('Stella Artois'))

    def test_name(self):
        self.assertEqual(PersonStatus.ALIVE.name, six.text_type('ALIVE'))
        self.assertEqual(LabelBeer.STELLA.name, six.text_type('STELLA'))

    def test_get(self):
        self.assertTrue(isinstance(PersonStatus.get(PersonStatus.ALIVE), Enum))
        self.assertTrue(isinstance(PersonStatus.get(six.text_type('ALIVE')), Enum))
        self.assertEqual(PersonStatus.get(PersonStatus.ALIVE), PersonStatus.get(six.text_type('ALIVE')))

    def test_choices(self):
        self.assertEqual(len(PersonStatus.choices()), len(PersonStatus))
        for value, member in PersonStatus.choices():
            self.assertTrue(isinstance(value, int))
            self.assertTrue(isinstance(member, PersonStatus))
            self.assertTrue(PersonStatus.get(value) == member)
        blank = PersonStatus.choices(blank=True)[0]
        self.assertEqual(blank, (BlankEnum.BLANK.value, BlankEnum.BLANK))

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
        self.assertEqual(PersonStatus.get(PersonStatus.ALIVE), PersonStatus.get(PersonStatus.ALIVE))

    def test_labels(self):
        self.assertEqual(LabelBeer.JUPILER.name, LabelBeer.JUPILER.label)
        self.assertNotEqual(LabelBeer.STELLA.name, LabelBeer.STELLA.label)
        self.assertTrue(isinstance(LabelBeer.STELLA.label, six.string_types))
        self.assertEqual(LabelBeer.STELLA.label,
                         six.text_type('Stella Artois'))

    def test_hash(self):
        self.assertTrue({LabelBeer.JUPILER: True}[LabelBeer.JUPILER])
