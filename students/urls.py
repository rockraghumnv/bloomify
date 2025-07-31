from django.urls import path
from students.views.dashboard import StudentDashboardView
from students.views.quiz import StartDynamicQuizView, DynamicQuizView
from students.views.results import QuizResultsView
from students.views.my_results import MyResultsView

app_name = 'students'

urlpatterns = [
    path('', StudentDashboardView.as_view(), name='dashboard'),
    path('start-dynamic-quiz/', StartDynamicQuizView.as_view(), name='start_dynamic_quiz'),
    path('dynamic-quiz/', DynamicQuizView.as_view(), name='dynamic_quiz'),
    path('quiz-complete/<int:quiz_id>/', QuizResultsView.as_view(), name='quiz_complete'),
    path('my-results/', MyResultsView.as_view(), name='my_results'),
]
