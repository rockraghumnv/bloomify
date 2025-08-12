from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from teachers.models import Syllabus
import google.generativeai as genai
from rest_framework.views import APIView
from django.http import HttpResponse

@method_decorator(login_required, name='dispatch')
class StartDynamicQuizView(APIView):
    def post(self, request):
        syllabus_id = request.POST.get('syllabus')
        num_per_taxonomy = int(request.POST.get('num_per_taxonomy', 3))
        
        if not syllabus_id:
            messages.error(request, 'Please select a syllabus.')
            return redirect('students:dashboard')
            
        try:
            syllabus = Syllabus.objects.get(id=syllabus_id)
        except Syllabus.DoesNotExist:
            messages.error(request, 'The selected syllabus does not exist.')
            return redirect('students:dashboard')
        
        # Get teacher from the selected syllabus
        teacher_id = syllabus.teacher.id
        
        request.session['quiz_teacher_id'] = teacher_id
        request.session['quiz_syllabus_id'] = syllabus_id
        request.session['quiz_num_per_taxonomy'] = num_per_taxonomy
        request.session['quiz_progress'] = {
            'taxonomy_index': 0,
            'current_count': 0,
            'correct_in_level': 0,
            'wrong_in_level': 0,
            'history': []
        }
        return redirect('students:dynamic_quiz')
    def get(self, request):
        return redirect('students:dashboard')

@method_decorator(login_required, name='dispatch')
class DynamicQuizView(APIView):
    def get(self, request):
        from .dynamic_quiz_logic import handle_dynamic_quiz
        resp = handle_dynamic_quiz(request)
        if resp is None:
            return HttpResponse('An error occurred in quiz logic.', status=500)
        return resp
    def post(self, request):
        from .dynamic_quiz_logic import handle_dynamic_quiz
        resp = handle_dynamic_quiz(request)
        if resp is None:
            return HttpResponse('An error occurred in quiz logic.', status=500)
        return resp

@login_required
def start_descriptive_quiz(request):
    """
    This view STARTS the new Descriptive quiz. It clears any old descriptive
    quiz state from the session and sets up the new one.
    """
    if request.method == 'POST':
        # --- THOROUGHLY CLEAR ALL PREVIOUS QUIZ DATA ---
        # Note the different session key 'desc_quiz_state' to keep the quiz types separate
        request.session.pop('desc_quiz_state', None)
        request.session.pop('current_question_data', None)
        request.session.pop('quiz_teacher_id', None)
        request.session.pop('quiz_syllabus_id', None)
        request.session.pop('quiz_num_per_taxonomy', None)
        
        syllabus_id = request.POST.get('syllabus_id')
        num_questions = request.POST.get('num_questions', '3')

        if not syllabus_id:
            messages.error(request, "Please select a syllabus to start the quiz.")
            return redirect('students:dashboard')

        try:
            syllabus = Syllabus.objects.get(id=syllabus_id)
        except Syllabus.DoesNotExist:
            messages.error(request, "The selected syllabus does not exist.")
            return redirect('students:dashboard')

        # Set the new quiz parameters in the session (can be shared with the MCQ quiz)
        request.session['quiz_teacher_id'] = syllabus.teacher.id
        request.session['quiz_syllabus_id'] = syllabus.id
        request.session['quiz_num_per_taxonomy'] = num_questions

        return redirect('students:descriptive_quiz')
    
    return redirect('students:dashboard')
