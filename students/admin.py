from django.contrib import admin
from .models import StudentResponse, StudentFeedback

@admin.register(StudentResponse)
class StudentResponseAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'question', 'is_correct', 'submitted_at']
    list_filter = ['is_correct', 'submitted_at', 'quiz']
    search_fields = ['student__username', 'student__email', 'quiz__title', 'student_name', 'student_usn']
    readonly_fields = ['submitted_at']
    
    fieldsets = (
        ('Response Information', {
            'fields': ('student', 'quiz', 'question', 'selected_answer', 'is_correct')
        }),
        ('Anonymous User Info', {
            'fields': ('student_name', 'student_college', 'student_usn'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('submitted_at',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'quiz', 'question')

@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'quiz', 'overall_score', 'remember_score', 
        'understand_score', 'apply_score', 'generated_at'
    ]
    list_filter = ['generated_at', 'quiz']
    search_fields = ['student__username', 'student__email', 'quiz__title']
    readonly_fields = ['generated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'quiz')
        }),
        ('Bloom\'s Taxonomy Scores', {
            'fields': (
                'remember_score', 'understand_score', 'apply_score', 
                'analyze_score', 'evaluate_score', 'create_score'
            )
        }),
        ('Overall Performance', {
            'fields': ('overall_score', 'feedback_text')
        }),
        ('Timestamp', {
            'fields': ('generated_at',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'quiz')
