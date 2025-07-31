from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from teachers.models import Quiz
from students.models import StudentResponse
from rest_framework.views import APIView

@method_decorator(login_required, name='dispatch')
class QuizResultsView(APIView):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        responses = StudentResponse.objects.filter(student=request.user, quiz=quiz)
        correct_count = responses.filter(is_correct=True).count()
        total_questions = responses.count()
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        student_name = request.session.get('student_name', request.user.first_name)
        student_college = request.session.get('student_college', '')
        return render(request, 'students/quiz_complete.html', {
            'quiz': quiz,
            'score': score,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'student_name': student_name,
            'student_college': student_college
        })
