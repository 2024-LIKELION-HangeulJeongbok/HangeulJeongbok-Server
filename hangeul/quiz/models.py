from django.db import models

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    options = models.JSONField(default=list)  # 선택지 저장
    answer = models.IntegerField()

    def __str__(self):
        return self.title