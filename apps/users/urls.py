from apps.users import views
from django.urls import path

urlpatterns = [
    path('userLogin/', views.LoginAPIVIew.as_view()),

]
