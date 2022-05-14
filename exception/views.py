from django.utils import http
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.views import exception_handler

from exception.enums import AuthMessage
from wallet.utils import response_fail
from rest_framework import status


def custom_exception_handler(exc, context):
    status_code = status.HTTP_400_BAD_REQUEST
    data = {}
    if isinstance(exc, AuthenticationFailed):
        data = str(exc.detail[0])
        status_code = exc.status_code
    elif isinstance(exc, ValidationError):
        data = str(exc.detail[0])
        status_code = exc.status_code
    else:
        return exception_handler(exc, context)
    response = response_fail(data, status_code)

    return response
