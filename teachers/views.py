from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Syllabus

@login_required
def dashboard(request):
    syllabi = Syllabus.objects.filter(teacher=request.user)
    return render(request, 'teachers/dashboard.html', {'syllabi': syllabi})

@login_required
def upload_syllabus(request):
    if request.method == 'POST':
        teacher_name = request.POST.get('teacher_name')
        college = request.POST.get('college')
        title = request.POST.get('title')
        content = request.POST.get('content')
        pdf_file = request.FILES.get('pdf_file')
        
        Syllabus.objects.create(
            teacher=request.user,
            teacher_name=teacher_name,
            college=college,
            title=title,
            content=content,
            pdf_file=pdf_file
        )
        messages.success(request, 'Syllabus uploaded successfully!')
        return redirect('teachers:dashboard')
    
    return render(request, 'teachers/upload_syllabus.html')
