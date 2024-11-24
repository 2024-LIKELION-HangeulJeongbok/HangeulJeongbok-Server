from rest_framework import serializers
from .models import Quiz

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id','title', 'body', 'options']

# 사용자의 답안이 맞는지 확인하는 답안제출 시리얼라이저
class AnswerSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    selected_option = serializers.IntegerField()

    def validate(self, data):
        try:
            quiz = Quiz.objects.get(id=data['quiz_id'])
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz not found.")

        if data['selected_option'] < 0 or data['selected_option'] >= len(quiz.options):
            raise serializers.ValidationError("Invalid option selected.")
        return data

    def check_answer(self):
        quiz = Quiz.objects.get(id=self.validated_data['quiz_id'])
        selected_option = self.validated_data['selected_option']
        return selected_option == quiz.answer  # True: 맞음, False: 틀림
