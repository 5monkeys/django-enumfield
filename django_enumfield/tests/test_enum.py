from django.contrib.formtools.tests import DummyRequest
from django.db import IntegrityError
from django.forms import ModelForm, TypedChoiceField
from django.test import TestCase
from django_enumfield.db.fields import EnumField
from django_enumfield.enum import Enum
from django_enumfield.exceptions import InvalidStatusOperationError
from django_enumfield.tests.models import Person, PersonStatus, Lamp, LampState, Beer, BeerStyle, BeerState


class EnumFieldTest(TestCase):

    def test_enum_field_init(self):
        field = EnumField(PersonStatus)
        self.assertEqual(field.default, PersonStatus.UNBORN)
        self.assertEqual(len(PersonStatus.choices()), len(field.choices))
        field = EnumField(PersonStatus, default=PersonStatus.ALIVE)
        self.assertEqual(field.default, PersonStatus.ALIVE)

    def test_enum_field_save(self):
        # Test model with EnumField WITHOUT _transitions
        lamp = Lamp.objects.create()
        self.assertEqual(lamp.state, LampState.OFF)
        lamp.state = LampState.ON
        lamp.save()
        self.assertEqual(lamp.state, LampState.ON)
        self.assertEqual(lamp.state, 1)

        self.assertRaises(InvalidStatusOperationError, setattr, lamp, 'state', 99)

        # Test model with EnumField WITH _transitions
        person = Person.objects.create()
        pk = person.pk
        self.assertEqual(person.status, PersonStatus.ALIVE)
        person.status = PersonStatus.DEAD
        person.save()
        self.assertTrue(isinstance(person.status, int))
        self.assertEqual(person.status, PersonStatus.DEAD)

        person = Person.objects.get(pk=pk)
        self.assertEqual(person.status, PersonStatus.DEAD)
        self.assertTrue(isinstance(person.status, int))

        self.assertRaises(InvalidStatusOperationError, setattr, person, 'status', 99)

        person = Person.objects.create(status=PersonStatus.ALIVE)
        self.assertRaises(InvalidStatusOperationError, setattr, person, 'status', PersonStatus.UNBORN)

        person.status = PersonStatus.DEAD
        self.assertEqual(person.save(), 'Person.save')

        self.assertTrue(Person.objects.filter(status=PersonStatus.DEAD).exists())
        beer = Beer.objects.create()
        beer.style = BeerStyle.LAGER
        self.assertEqual(beer.state, BeerState.FIZZY)
        beer.save()

    def test_magic_model_properties(self):
        beer = Beer.objects.create(style=BeerStyle.WEISSBIER)
        self.assertEqual(getattr(beer, 'get_style_display')(), 'Weissbier')

    def test_enum_field_del(self):
        lamp = Lamp.objects.create()
        del lamp.state
        self.assertEqual(lamp.state, None)
        self.assertRaises(IntegrityError, lamp.save)
        beer = Beer.objects.create()
        beer.style = BeerStyle.STOUT
        beer.state = None
        beer.save()
        self.assertEqual(beer.state, None)
        self.assertEqual(beer.style, BeerStyle.STOUT)

    def test_enum_field_modelform(self):
        person = Person.objects.create()

        class PersonForm(ModelForm):
            class Meta:
                model = Person

        request = DummyRequest()
        request.POST['status'] = u'2'
        form = PersonForm(request.POST, instance=person)
        self.assertTrue(isinstance(form.fields['status'], TypedChoiceField))
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(person.status, PersonStatus.DEAD)

        request.POST['status'] = u'99'
        form = PersonForm(request.POST, instance=person)
        self.assertFalse(form.is_valid())


class EnumTest(TestCase):

    def test_label(self):
        self.assertEqual(PersonStatus.label(PersonStatus.ALIVE), u'Alive')

    def test_name(self):
        self.assertEqual(PersonStatus.name(PersonStatus.ALIVE), u'ALIVE')

    def test_get(self):
        self.assertTrue(isinstance(PersonStatus.get(PersonStatus.ALIVE), Enum.Value))
        self.assertTrue(isinstance(PersonStatus.get(u'ALIVE'), Enum.Value))
        self.assertEqual(unicode(PersonStatus.get(PersonStatus.ALIVE)), PersonStatus.label(PersonStatus.ALIVE))

    def test_choices(self):
        self.assertEqual(len(PersonStatus.choices()), len(PersonStatus.items()))
        self.assertTrue(all(key in PersonStatus.__dict__ for key in dict(PersonStatus.items())))

    def test_default(self):
        self.assertEqual(PersonStatus.default(), PersonStatus.UNBORN)

    def test_field(self):
        self.assertTrue(isinstance(PersonStatus.field(), EnumField))

    def test_equal(self):
        self.assertTrue(PersonStatus.ALIVE == PersonStatus.ALIVE)
        self.assertFalse(PersonStatus.ALIVE == PersonStatus.DEAD)
        self.assertEqual(PersonStatus.get(PersonStatus.ALIVE), PersonStatus.get(PersonStatus.ALIVE))
