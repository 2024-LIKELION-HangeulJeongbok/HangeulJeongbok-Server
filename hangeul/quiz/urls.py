from django.urls import path
from .views import *

urlpatterns = [
    path('quizes/', QuizListAPIView.as_view(), name='quiz-list'),
]
