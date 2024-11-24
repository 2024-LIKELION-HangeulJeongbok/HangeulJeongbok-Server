from django.urls import path
from .views import QuizListAPIView, QuizAnswerAPIView, QuizResultAPIView

urlpatterns = [
    path('quizzes/', QuizListAPIView.as_view(), name='quiz-list'),  # 퀴즈 목록 조회
    path('quizzes/answer/', QuizAnswerAPIView.as_view(), name='quiz-answer'),  # 정답 제출
    path('quiz/results/', QuizResultAPIView.as_view(), name='quiz-results'),
]
