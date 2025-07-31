from django.db import models
from django.contrib.auth.models import User

class Syllabus(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='syllabus/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Quiz(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    num_questions = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    access_link = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.title} - {self.syllabus.title}"

class Question(models.Model):
    BLOOM_LEVELS = [
        ('remember', 'Remember'),
        ('understand', 'Understand'),
        ('apply', 'Apply'),
        ('analyze', 'Analyze'),
        ('evaluate', 'Evaluate'),
        ('create', 'Create'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()
    bloom_level = models.CharField(max_length=20, choices=BLOOM_LEVELS)
    correct_answer = models.CharField(max_length=200)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.question_text[:50]}..."
