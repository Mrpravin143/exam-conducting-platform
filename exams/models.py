from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings



# make your models


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    exam_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)  # exam duration

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('DESC', 'Descriptive'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default="MCQ")
    marks = models.IntegerField(default=1)

    # For MCQ
    option1 = models.CharField(max_length=255, blank=True, null=True)
    option2 = models.CharField(max_length=255, blank=True, null=True)
    option3 = models.CharField(max_length=255, blank=True, null=True)
    option4 = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.exam.title} - {self.text[:50]}"



class StudentExamSession(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    start_time = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


class StudentAnswer(models.Model):
    session = models.ForeignKey(StudentExamSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_option = models.CharField(max_length=255, blank=True, null=True)
    marks_obtained = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.session.student.username} - {self.question.text[:30]}"









