from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response


class ADDQuestionsView(CreateAPIView,UpdateAPIView):

    def create(self, request, *args, **kwargs):
        return Response()


