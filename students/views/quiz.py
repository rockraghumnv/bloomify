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
        teacher_id = request.POST.get('teacher')
        syllabus_id = request.POST.get('syllabus')
        num_per_taxonomy = int(request.POST.get('num_per_taxonomy', 3))
        if not (teacher_id and syllabus_id):
            messages.error(request, 'Please select both teacher and syllabus.')
            return redirect('students:dashboard')
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
