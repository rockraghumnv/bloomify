from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/', views.register, name='register'),
]

