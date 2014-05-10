from django.core.exceptions import ValidationError


class InvalidStatusOperationError(ValidationError):
    pass
