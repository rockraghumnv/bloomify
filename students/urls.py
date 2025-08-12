from django.urls import path
from students.views.dashboard import StudentDashboardView
from students.views.quiz import StartDynamicQuizView, DynamicQuizView, start_descriptive_quiz
from students.views.results import QuizResultsView
from students.views.my_results import MyResultsView
from students.views import descriptive_quiz_logic

app_name = 'students'

urlpatterns = [
    path('', StudentDashboardView.as_view(), name='dashboard'),
    path('start-dynamic-quiz/', StartDynamicQuizView.as_view(), name='start_dynamic_quiz'),
    path('dynamic-quiz/', DynamicQuizView.as_view(), name='dynamic_quiz'),
    path('quiz-complete/<int:quiz_id>/', QuizResultsView.as_view(), name='quiz_complete'),
    path('my-results/', MyResultsView.as_view(), name='my_results'),
    path('start-descriptive-quiz/', start_descriptive_quiz, name='start_descriptive_quiz'),
    path('descriptive-quiz/', descriptive_quiz_logic.handle_descriptive_quiz, name='descriptive_quiz'),


]
