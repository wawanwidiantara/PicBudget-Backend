from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


def full_details_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if isinstance(exc, APIException) and response is not None:

        response.data = {"errors": response.data}

    return response
