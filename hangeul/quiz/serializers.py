from rest_framework import serializers
from .models import Quiz

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'question', 'options']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        options = representation['options']

        # 쉼표 기준으로 인덱스 값 추가(python 내장함수 enumerate사용)
        formatted_options = [
            f"{idx + 1}. {option}" for idx, option in enumerate(options)
        ]

        representation['options'] = formatted_options
        return representation

# 사용자의 답안이 맞는지 확인하는 답안제출 시리얼라이저
class AnswerSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    selected_option = serializers.IntegerField()

    def validate(self, data):
        try:
            quiz = Quiz.objects.get(id=data['quiz_id'])
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz not found.")

        # 선택지값이 선택지 총문항보다 많거나 1보다 작지 말아야함.
        if data['selected_option'] < 0 or data['selected_option'] >= len(quiz.options):
            raise serializers.ValidationError("Invalid option selected.")
        return data

    def check_answer(self):
        quiz_id = self.validated_data['quiz_id']
        user_answer = self.validated_data['selected_option']

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            return quiz.answer == user_answer
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Invalid quiz ID")
