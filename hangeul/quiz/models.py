from django.db import models

# 퀴즈 내용 데이터베이스에 저장(문제, 선택지, 답안)
class Quiz(models.Model):
    question = models.TextField()
    options = models.JSONField(default=list)  # 선택지 저장
    answer = models.IntegerField()
    # score = models.IntegerField(default=0)

    def __str__(self):
        return self.question