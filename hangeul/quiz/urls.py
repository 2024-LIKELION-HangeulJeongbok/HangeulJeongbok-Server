from django.urls import path
from .views import *

urlpatterns = [
    path('quizes/', QuizListAPIView.as_view(), name='quiz-list'),  # 퀴즈 목록 조회
    path('results/', QuizResultAPIView.as_view(), name='quiz-results'),
]
