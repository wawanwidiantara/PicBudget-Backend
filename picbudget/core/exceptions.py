from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if isinstance(exc, APIException) and response is not None:

        full_details = exc.get_full_details()

        response.data = {"errors": full_details}

    return response
