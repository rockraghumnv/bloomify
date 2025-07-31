from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload-syllabus/', views.upload_syllabus, name='upload_syllabus'),
]
