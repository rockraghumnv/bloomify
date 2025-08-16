from django.db import models
from django.contrib.auth.models import User
from teachers.models import Syllabus

class QuizFeedback(models.Model):
    QUIZ_TYPES = [
        ('mcq', 'Multiple Choice Questions'),
        ('descriptive', 'Descriptive Questions'),
    ]
    
    FEEDBACK_LEVELS = [
        ('basic', 'Basic Knowledge'),
        ('intermediate', 'Intermediate Knowledge'), 
        ('advanced', 'Advanced Knowledge'),
        ('excellent', 'Excellent Knowledge'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_feedbacks')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedbacks')
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES)
    max_level_reached = models.IntegerField(default=0)  # 0-5 (representing remember to create)
    feedback_level = models.CharField(max_length=20, choices=FEEDBACK_LEVELS)
    feedback_message = models.TextField()
    
    total_questions_attempted = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)
    accuracy_percentage = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz_type} - Level {self.max_level_reached}"

class QuizQuestionResult(models.Model):
    feedback = models.ForeignKey(QuizFeedback, on_delete=models.CASCADE, related_name='question_results')
    
    bloom_level = models.CharField(max_length=20)  # remember, understand, apply, etc.
    question_text = models.TextField()
    student_answer = models.TextField()
    
    # For MCQ questions
    correct_option = models.CharField(max_length=500, blank=True, null=True)
    selected_option = models.CharField(max_length=500, blank=True, null=True)
    
    # For Descriptive questions
    expected_keywords = models.JSONField(blank=True, null=True)  # Store as list
    matched_keywords = models.JSONField(blank=True, null=True)  # Store matching details
    
    is_correct = models.BooleanField(default=False)
    score_percentage = models.FloatField(default=0.0)
    topic = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.feedback.student.username} - {self.bloom_level} - {'✓' if self.is_correct else '✗'}"
