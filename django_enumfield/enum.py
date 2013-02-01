import logging
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django_enumfield.db.fields import EnumField


def translate(name):
    return smart_unicode(_(name.replace('_', ' ').lower())).title()

logger = logging.getLogger(__name__)


class EnumType(type):

    def __new__(cls, *args, **kwargs):
        """
        Create enum values from all uppercase class attributes and store them in a dict on the Enum class.
        """
        enum = super(EnumType, cls).__new__(cls, *args, **kwargs)
        attributes = filter(lambda (k, v): k.isupper(), enum.__dict__.iteritems())
        enum.values = {}
        for attribute in attributes:
            enum.values[attribute[1]] = enum.Value(attribute[0], attribute[1], enum)
        return enum


class Enum(object):
    """
    A container for holding and restoring enum values.
    Usage:
        class BeerStyle(Enum):
            LAGER = 0
            STOUT = 1
            WEISSBIER = 2
    It can also validate enum value transitions by defining the _transitions variable as a dict with transitions.
    """
    __metaclass__ = EnumType

    class Value(object):
        """
        A value represents a key value pair with a uppercase name and a integer value:
        GENDER = 1
        "name" is a upper case string representing the class attribute
        "label" is a translatable human readable version of "name"
        "enum_type" is the value defined for the class attribute
        """
        def __init__(self, name, value, enum_type):
            self.name = name
            self.label = translate(name)
            self.value = value
            self.enum_type = enum_type

        def __unicode__(self):
            return unicode(self.label)

        def __str__(self):
            return self.label

        def __repr__(self):
            return self.label

        def __eq__(self, other):
            if other and isinstance(other, Enum.Value):
                return self.value == other.value
            else:
                raise TypeError('Can not compare Enum with %s' % other.__class__.__name__)

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples with the value as first argument and the value container class as second argument.
        """
        return sorted(cls.values.iteritems(), key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        Usage:
            IntegerField(choices=my_enum.choices(), default=my_enum.default(), ...
        """
        return cls.choices()[0][0]

    @classmethod
    def field(cls, **kwargs):
        """
        A shortcut for
        Usage:
            class MyModelStatuses(Enum):
                UNKNOWN = 0
            class MyModel(Model):
                status = MyModelStatuses.field()
        """
        return EnumField(cls, **kwargs)

    @classmethod
    def get(cls, name_or_numeric):
        """
        Will return a Enum.Value matching the value argument.
        """
        if isinstance(name_or_numeric, basestring):
            name_or_numeric = getattr(cls, name_or_numeric.upper())

        return cls.values.get(name_or_numeric)

    @classmethod
    def name(cls, numeric):
        """
        Will return the uppercase name for the matching Enum.Value.
        """
        return cls.get(numeric).name

    @classmethod
    def label(cls, numeric):
        """
        Will return the human readable label for the matching Enum.Value.
        """
        return translate(unicode(cls.get(numeric)))

    @classmethod
    def items(cls):
        """
        Will return a list of tuples consisting of every enum value in the form [('NAME', value), ...]
        """
        items = [(value.name, key) for key, value in cls.values.iteritems()]
        return sorted(items, key=lambda x: x[1])

    @classmethod
    def is_valid_transition(cls, from_value, to_value):
        """
        Will check if to_value is a valid transition from from_value. Returns true if it is a valid transition.
        """
        return from_value == to_value or from_value in cls.transition_origins(to_value)

    @classmethod
    def transition_origins(cls, to_value):
        """
        Returns all values the to_value can make a transition from.
        """
        return cls._transitions[to_value]
