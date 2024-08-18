from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response


class Exception_(Exception):
    default_code = 4000
    default_message = "错误"

    def __init__(self, message=None, code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code


def exception_handler(exc, context):
    if isinstance(exc, Exception_):
        status_code = status.HTTP_400_BAD_REQUEST
        return Response(data={"code": exc.code,
                              "detail": exc.message}, status=status_code)

    return drf_exception_handler(exc, context)