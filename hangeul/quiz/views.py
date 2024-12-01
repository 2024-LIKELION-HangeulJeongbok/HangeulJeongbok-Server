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

# 퀴즈 목록 API, 정답 제출, 다음 퀴즈로 이동, 그리고 퀴즈 완료 후 결과 반환
class QuizListAPIView(APIView):
    def get(self, request):
        user_id = request.user.id
        session_key = f'quiz_data_{user_id}'  # 각 유저별 세션 키를 사용

        # 세션에 유저의 퀴즈 데이터가 없으면 초기화
        if session_key not in request.session:
            quiz_ids = list(Quiz.objects.values_list('id', flat=True))  # 퀴즈 아이디 목록
            request.session[session_key] = {
                'current_quiz_index': 0,
                'score': 0,
                'wrong_answers': [],
                'quiz_ids': quiz_ids,
            }

        # 세션 데이터 가져오기
        user_quiz_data = request.session[session_key]

        # 퀴즈 완료 여부 확인
        current_index = user_quiz_data['current_quiz_index']
        quiz_ids = user_quiz_data['quiz_ids']

        if current_index >= len(quiz_ids):
            wrong_quizzes = Quiz.objects.filter(id__in=user_quiz_data['wrong_answers'])
            wrong_serializer = QuizSerializer(wrong_quizzes, many=True)
            return Response({
                "message": "Quiz completed.",
                "final_score": user_quiz_data['score'],
                "total_score": len(quiz_ids) * 5,  # 점수 환산
                "wrong_answers": wrong_serializer.data
            }, status=status.HTTP_200_OK)

        # 현재 문제 반환
        quiz = Quiz.objects.get(id=quiz_ids[current_index])
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.user.id
        session_key = f'quiz_data_{user_id}'  # 각 유저별 세션 키를 사용
        user_quiz_data = request.session.get(session_key, {})

        # 퀴즈가 끝난 상태에서는 더 이상 응답하지 않음
        if user_quiz_data.get('current_quiz_index', 0) >= len(user_quiz_data.get('quiz_ids', [])):
            return Response({
                'message': 'No more quizzes available.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # AnswerSerializer를 사용하여 유효성 검사
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            quiz = Quiz.objects.get(id=request.data.get('quiz_id'))
            # 실제 옵션 개수와 사용자가 선택한 옵션이 일치하는지 확인
            options_count = len(quiz.options)

            # selected_option이 유효한지 확인
            selected_option = request.data.get('selected_option')
            if selected_option < 1 or selected_option > options_count:
                return Response({
                    'error': f'Selected option {selected_option} is out of range. Please choose between 1 and {options_count}.'
                }, status=status.HTTP_400_BAD_REQUEST)

            is_correct = serializer.check_answer()
            if is_correct:
                user_quiz_data['score'] += 1
                result = "O"
            else:
                current_index = user_quiz_data['current_quiz_index']
                user_quiz_data['wrong_answers'].append(user_quiz_data['quiz_ids'][current_index])
                result = "X"

            # 다음 문제로 이동
            user_quiz_data['current_quiz_index'] += 1
            request.session[session_key] = user_quiz_data  # 세션 저장

            # 퀴즈 완료 확인
            if user_quiz_data['current_quiz_index'] >= len(user_quiz_data['quiz_ids']):
                return Response({
                    'result': result,
                    'message': "All quizzes completed. Proceed to results."
                }, status=status.HTTP_200_OK)

            # 다음 문제 반환
            next_quiz_id = user_quiz_data['quiz_ids'][user_quiz_data['current_quiz_index']]
            next_quiz = Quiz.objects.get(id=next_quiz_id)
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
