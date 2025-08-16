from django.contrib import admin
from .models import QuizFeedback, QuizQuestionResult

@admin.register(QuizFeedback)
class QuizFeedbackAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz_type', 'feedback_level', 'max_level_reached', 'accuracy_percentage', 'created_at']
    list_filter = ['quiz_type', 'feedback_level', 'created_at', 'teacher']
    search_fields = ['student__username', 'student__email', 'syllabus__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'teacher', 'syllabus', 'quiz_type')
        }),
        ('Performance', {
            'fields': ('max_level_reached', 'feedback_level', 'total_questions_attempted', 'total_correct_answers', 'accuracy_percentage')
        }),
        ('Feedback', {
            'fields': ('feedback_message',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(QuizQuestionResult)
class QuizQuestionResultAdmin(admin.ModelAdmin):
    list_display = ['feedback', 'bloom_level', 'is_correct', 'score_percentage', 'topic', 'created_at']
    list_filter = ['bloom_level', 'is_correct', 'feedback__quiz_type', 'created_at']
    search_fields = ['question_text', 'feedback__student__username', 'topic']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('feedback', 'bloom_level', 'question_text', 'topic')
        }),
        ('Student Response', {
            'fields': ('student_answer', 'is_correct', 'score_percentage')
        }),
        ('MCQ Details', {
            'fields': ('correct_option', 'selected_option'),
            'classes': ('collapse',)
        }),
        ('Descriptive Details', {
            'fields': ('expected_keywords', 'matched_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
