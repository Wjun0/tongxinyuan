
from django.urls import path, re_path
from apps.questions import views

urlpatterns = [
    re_path(r'^add_question_type/$', views.ADDQuestionsTypeView.as_view()),
    re_path(r'^add_question/$', views.ADDQuestionsView.as_view()),





    # 查询接口
    re_path(r'^index/$', views.IndexView.as_view()),
]