from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from teachers.models import Quiz
from students.models import StudentResponse
from rest_framework.views import APIView

@method_decorator(login_required, name='dispatch')
class MyResultsView(APIView):
    def get(self, request):
        completed_quizzes = Quiz.objects.filter(studentresponse__student=request.user).distinct()
        results = []
        for quiz in completed_quizzes:
            responses = StudentResponse.objects.filter(student=request.user, quiz=quiz)
            correct_count = responses.filter(is_correct=True).count()
            total_questions = responses.count()
            score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            results.append({
                'quiz': quiz,
                'score': score,
                'correct_count': correct_count,
                'total_questions': total_questions
            })
        return render(request, 'students/my_results.html', {'results': results})
