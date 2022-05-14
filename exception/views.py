from django.utils import http
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken

from exception.enums import AuthMessage
from wallet.utils import response_fail
from rest_framework import status


def custom_exception_handler(exc, context):

    if isinstance(exc, InvalidToken):
        data = 'Token is invalid or expired.'
        status_code = exc.status_code
    else:
        data = str(exc.detail[0]) if isinstance(exc.detail, (tuple, list,)) else str(exc.detail)
        status_code = exc.status_code

    response = response_fail(data, status_code)

    return response
