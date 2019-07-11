# Changelog


## [2.0.0]

- The ``enumfield.enum.Enum`` class is now a subclass of the native `IntEnum` 
shipped with Python 3.4 (uses the ``enum34`` package on previous versions of Python)
- Renamed `_labels` to `__labels__`
- Renamed `_transitions` to `__transitions__`
- Removed the classmethods `Enum.name()` and `Enum.label()` since they are now 
over-shadowed by properties on the enum instance.
- Converted README.rst to markdown (README.md)
- Added Django 2.2 support
- Dropped support for Django < 1.11

## [1.5.0]

- Added Django 2.1 support
- Added Python 3.7 support
- Dropped Python 3.3 support

## [1.4.0]

- Added Django 1.11 support (from [#43](https://github.com/5monkeys/django-enumfield/pull/43))
- Added Python 3.6 support
- Dropped support for Django < 1.8
