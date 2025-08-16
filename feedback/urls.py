from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('view/<int:quiz_id>/', views.view_feedback, name='view_feedback'),
    path('generate/<int:quiz_id>/', views.generate_feedback, name='generate_feedback'),
    # New comprehensive feedback URLs
    path('detailed/<int:feedback_id>/', views.detailed_feedback, name='detailed_feedback'),
    path('history/', views.feedback_history, name='feedback_history'),
]
