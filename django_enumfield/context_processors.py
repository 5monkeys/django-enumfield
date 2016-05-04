import inspect

from django_enumfield import enum

from django.apps import apps
from django.utils import lru_cache, module_loading

def enum_context(request):
    return {'enums': get_enums()}

@lru_cache.lru_cache()
def get_enums():
    result = TemplateErrorDict("Unknown app label %s")

    for app_config in apps.get_app_configs():
        if not module_loading.module_has_submodule(app_config.module, 'enums'):
            continue

        module = module_loading.import_module('.enums', app_config.name)

        for k, v in inspect.getmembers(module):
            if not inspect.isclass(v):
                continue

            if not issubclass(v, enum.Enum):
                continue

            result.setdefault(
                app_config.label,
                TemplateErrorDict("Unknown enum %%r in %r app" % app_config.label),
            )[k] = v

    return result

class TemplateErrorException(RuntimeError):
    silent_variable_failure = False

class TemplateErrorDict(dict):
    """
    Like a regular dict but raises our own exception instead of
    ``KeyError`` to bypass Django's silent variable swallowing.
    """

    def __init__(self, message, *args, **kwargs):
        self.message = message

        super(TemplateErrorDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key not in self:
            raise TemplateErrorException(self.message % key)

        return super(TemplateErrorDict, self).__getitem__(key)
