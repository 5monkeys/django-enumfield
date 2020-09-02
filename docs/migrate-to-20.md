# Migrate to 2.0

`django-enumfield` 2.0 migrated to use native [IntEnums](https://docs.python.org/3/library/enum.html#enum.IntEnum)

Changes needed:
* `labels` to `__labels__`
* `_transitions` to `__transitions__`
* Any custom property need to be converted to class properties.
* `__default__` should be set to the first enum value, that was the default before

**Before:**
```python
from django_enumfield.enum import Enum


class MyEnum(Enum):
    FIRST = 1
    SECOND = 2
    
    labels = {FIRST: "1st", SECOND: "2nd"}
    _transitions = {SECOND: (FIRST,)}
    
    values_that_are_first = (FIRST,)
```

**After:**
```python
from django_enumfield.enum import Enum
from django.utils.functional import classproperty


class MyEnum(Enum):
    FIRST = 1
    SECOND = 2
    
    # `labels` to `__labels__` and `_transitions` to `__transitions__`
    __labels__ = {FIRST: "1st", SECOND: "2nd"}
    __transitions__ = {SECOND: (FIRST,)}
    
    # Set the default (used by EnumField) to the first enum value.
    # This is only necessary if it isn't explicitly specified on the field.
    __default__ = FIRST

    @classproperty
    def values_that_are_first(cls): 
        return (cls.FIRST,)

# After Enum instantiation is fine as well (lookups are a bit faster) 
MyEnum.values_that_are_first = (MyEnum.FIRST,)
```