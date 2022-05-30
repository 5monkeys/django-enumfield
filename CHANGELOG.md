# Changelog

## [unreleased]

## [3.0.0]

- Move CI to GitHub Actions
- Dropped support for Python < 3.7
- Dropped support for Django < 2.2
- Added support for Django 3.2
- Added support for Python 3.10
- Added support for Django 4.0

## [2.0.2]

- Added Django 3.1 support. (Pull #63)

## [2.0.1]

- Fixed get_FIELD_display to handle `None`. (Pull #59)

## [2.0.0]

**Many breaking changes this release.**

- The ``enumfield.enum.Enum`` class is now a subclass of the native `IntEnum`
shipped with Python 3.4 (uses the ``enum34`` package on previous versions of Python)
- Renamed `labels` to `__labels__`
- Renamed `_transitions` to `__transitions__`
- Added aliases for the classmethods `Enum.name()` as `Enum.get_name()` and
`Enum.label()` as `Enum.get_label()`.  Access the old way
(`Enum.name()` and `Enum.label()`) is still supported though, but the new names
are easier to be discovered by IDEs for example.
- `Enum.get_label()` and `Enum.get_name()` now return None if the enum value was
not found instead of raising `AttributeError`
- `EnumField` does not automatically set a default which is the first enum value anymore.
Use `Enum.__default__ = VALUE` or pass it explicitly to `EnumField`
- Converted README.rst to markdown (README.md)
- Added Django 2.2 support
- Added Django 3.0b1 support
- Dropped support for Django < 1.11
- Added limited mypy support

## [1.5.0]

- Added Django 2.1 support
- Added Python 3.7 support
- Dropped Python 3.3 support

## [1.4.0]

- Added Django 1.11 support (from [#43](https://github.com/5monkeys/django-enumfield/pull/43))
- Added Python 3.6 support
- Dropped support for Django < 1.8
