from django.db import models
from django.contrib.auth.models import User
from teachers.models import Quiz, Question

class StudentResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    # New fields for anonymous users
    student_name = models.CharField(max_length=100, blank=True, null=True)
    student_college = models.CharField(max_length=200, blank=True, null=True)
    student_usn = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'quiz', 'question')

    def __str__(self):
        if self.student:
            return f"{self.student.username} - {self.quiz.title} - Q{self.question.id}"
        else:
            return f"{self.student_name or 'Anonymous'} - {self.quiz.title} - Q{self.question.id}"

class StudentFeedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    remember_score = models.FloatField(default=0.0)
    understand_score = models.FloatField(default=0.0)
    apply_score = models.FloatField(default=0.0)
    analyze_score = models.FloatField(default=0.0)
    evaluate_score = models.FloatField(default=0.0)
    create_score = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    feedback_text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'quiz')
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} Feedback"
