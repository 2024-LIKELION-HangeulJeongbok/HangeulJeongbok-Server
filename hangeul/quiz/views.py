from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz
from .serializers import QuizSerializer, AnswerSerializer

# 퀴즈 목록 API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz
from .serializers import QuizSerializer, AnswerSerializer

# 퀴즈 목록 및 진행 API
class QuizListAPIView(APIView):
    def get(self, request):
        # 세션에서 진행 상태 가져오기
        current_index = request.session.get('current_quiz_index', 0)
        quiz_ids = request.session.get('quiz_ids')

        # 첫 요청 시 퀴즈 ID 목록 초기화
        if not quiz_ids:
            quiz_ids = list(Quiz.objects.values_list('id', flat=True))
            request.session['quiz_ids'] = quiz_ids
            request.session['current_quiz_index'] = 0
            request.session['score'] = 0 # 총 점수 초기화
            request.session['wrong_answers'] = [] # 틀린 문제 ID

        # 퀴즈가 끝났다면 결과 페이지로 안내
        if current_index >= len(quiz_ids):
            total_questions = len(quiz_ids)
            final_score = request.session.get('score', 0)
            wrong_answers = request.session.get('wrong_answers', [])
            wrong_quizzes = Quiz.objects.filter(id__in=wrong_answers)

            # 틀린 문제를 반환
            wrong_serializer = QuizSerializer(wrong_quizzes, many=True)
            return Response({
                "message": "Quiz completed.",
                "final_score": final_score,
                "total_score": 100,  # 100점 만점
                "wrong_answers": wrong_serializer.data
            }, status=status.HTTP_200_OK)

        # 현재 문제 반환
        quiz = Quiz.objects.get(id=quiz_ids[current_index])
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            is_correct = serializer.check_answer()
            current_index = request.session.get('current_quiz_index', 0)
            quiz_ids = request.session.get('quiz_ids')

            # 점수 업데이트 및 틀린 문제 기록
            if is_correct:
                request.session['score'] += 1
                result = "O"
            else:
                request.session['wrong_answers'].append(quiz_ids[current_index])
                result = "X"

            # 다음 문제로 이동
            request.session['current_quiz_index'] += 1
            next_index = request.session['current_quiz_index']

            # 퀴즈 끝 여부 확인
            if next_index >= len(quiz_ids):
                return Response({
                    'result': result,
                    'message': "All quizzes completed. Proceed to results."
                }, status=status.HTTP_200_OK)

            # 다음 문제 데이터 가져오기
            next_quiz = Quiz.objects.get(id=quiz_ids[next_index])
            next_quiz_serializer = QuizSerializer(next_quiz)

            return Response({
                'result': result,
                'next_quiz': next_quiz_serializer.data
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
    def get(self, request):
        score = request.session.get('score', 0)
        quiz_ids = request.session.get('quiz_ids', [])
        wrong_answers = request.session.get('wrong_answers', [])

        wrong_quizzes = Quiz.objects.filter(id__in=wrong_answers)
        serializer = QuizSerializer(wrong_quizzes, many=True)

        return Response({
            'score': score,
            'total': len(quiz_ids),
            'wrong_answers': serializer.data
        }, status=status.HTTP_200_OK)
