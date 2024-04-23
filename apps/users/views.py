from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response


class LoginAPIVIew(CreateAPIView):
    def post(self, request, *args, **kwargs):
        return Response({"message": "ok"})
