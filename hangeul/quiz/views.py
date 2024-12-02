import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, QuizHistory
from .serializers import QuizSerializer, AnswerSerializer

# 퀴즈 목록 API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz
from .serializers import QuizSerializer, AnswerSerializer

# 퀴즈 목록 API, 정답 제출, 다음 퀴즈로 이동, 그리고 퀴즈 완료 후 결과 반환
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Quiz, QuizHistory
from .serializers import QuizSerializer, AnswerSerializer

class QuizListAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request):
        user = request.user
        
        # 유저의 진행 중인 퀴즈 이력을 가져옴
        quiz_history = QuizHistory.objects.filter(user=user, is_correct=None)

        if not quiz_history.exists():
            # 새로운 퀴즈 세션을 초기화
            quiz_ids = list(Quiz.objects.values_list('id', flat=True))
            random.shuffle(quiz_ids)  # 퀴즈 순서를 랜덤으로 섞기
            for quiz_id in quiz_ids:
                QuizHistory.objects.create(user=user, quiz_id=quiz_id, selected_option=-1, is_correct=None)

        # 진행 중인 퀴즈를 반환
        current_quiz_history = QuizHistory.objects.filter(user=user, is_correct=None).first()
        if current_quiz_history:
            quiz = current_quiz_history.quiz
            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # 모든 퀴즈가 완료되었으면 결과 반환
            correct_answer = QuizHistory.objects.filter(user=user, is_correct=True).count()
            final_score = correct_answer*5
            total_score = 100
            return Response({
                'message': "All quizzes completed.",
                'final_score': final_score,
                'total_score': total_score,
            }, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = request.data.get('quiz_id')
            selected_option = request.data.get('selected_option')
            quiz = Quiz.objects.get(id=quiz_id)
            
            # 현재 진행 중인 퀴즈 이력 가져오기
            quiz_history = QuizHistory.objects.get(user=user, quiz=quiz, is_correct=None)

            is_correct = (quiz.answer == selected_option)
            
            # 퀴즈 이력 업데이트
            quiz_history.selected_option = selected_option
            quiz_history.is_correct = is_correct
            quiz_history.save()

            # 다음 퀴즈로 이동
            next_quiz_history = QuizHistory.objects.filter(user=user, is_correct=None).first()
            
            # try:
            #     user_info = User.objects.get(sp_user_id = user_id)
            # except User.DoesNotExist:
            #     user_info = None

            if not next_quiz_history:
                final_score = QuizHistory.objects.filter(user=user, is_correct=True).count()
                total_questions = QuizHistory.objects.filter(user=user).count()
                return Response({
                    'result': "X" if not is_correct else "O",
                    'message': "All quizzes completed. Proceed to results.",
                    'final_score': final_score,
                    'total_score': total_questions,
                }, status=status.HTTP_200_OK)

            next_quiz = next_quiz_history.quiz
            next_quiz_serializer = QuizSerializer(next_quiz)
            return Response({
                'result': "O" if is_correct else "X",
                'next_quiz': next_quiz_serializer.data  # 다음 문제를 반환
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 응답 제출 API
class QuizAnswerAPIView(APIView):
    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            is_correct = serializer.check_answer()
            return Response({'result':'O' if is_correct else 'X'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 결과 확인 API
class QuizResultAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능
    def get(self, request):
        final_score = request.session.get('score', 0)
        quiz_ids = request.session.get('quiz_ids', [])
        wrong_answers = request.session.get('wrong_answers', [])

        # 총 문제 수*문항당 점수 환산
        total_score = len(quiz_ids)*5

        wrong_quizzes = Quiz.objects.filter(id__in=wrong_answers)
        serializer = QuizSerializer(wrong_quizzes, many=True)

        return Response({
            'result': f"{final_score}/{total_score}",
            'wrong_answers': serializer.data
        }, status=status.HTTP_200_OK)
