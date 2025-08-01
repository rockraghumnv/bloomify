from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('view/<int:quiz_id>/', views.view_feedback, name='view_feedback'),
    path('generate/<int:quiz_id>/', views.generate_feedback, name='generate_feedback'),
]
