
from django.urls import path, re_path
from apps.questions import views

urlpatterns = [
    re_path(r'^addQuestions/$', views.ADDQuestionsView.as_view()),
]