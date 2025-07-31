from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from teachers.models import Syllabus
from rest_framework.views import APIView

@method_decorator(login_required, name='dispatch')
class StudentDashboardView(APIView):
    def get(self, request):
        # Show teacher's full name if available, else username
        teachers = User.objects.filter(syllabus__isnull=False).distinct()
        teacher_display = {}
        for t in teachers:
            teacher_display[t.id] = t.get_full_name() or t.username
        syllabi = Syllabus.objects.all()
        selected_teacher_id = request.GET.get('teacher')
        selected_syllabus_id = request.GET.get('syllabus')
        num_per_taxonomy = request.GET.get('num_per_taxonomy', '3')
        filtered_syllabi = syllabi
        if selected_teacher_id:
            filtered_syllabi = syllabi.filter(teacher_id=selected_teacher_id)
        # Re-query teachers to include any new ones after syllabus creation
        teachers = User.objects.filter(syllabus__isnull=False).distinct()
        return render(request, 'students/dashboard.html', {
            'teachers': teachers,
            'teacher_display': teacher_display,
            'syllabi': filtered_syllabi,
            'selected_teacher_id': selected_teacher_id,
            'selected_syllabus_id': selected_syllabus_id,
            'num_per_taxonomy': num_per_taxonomy
        })
