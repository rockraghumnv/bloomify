from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')
    return render(request, 'registration/register.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def register_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            group, _ = Group.objects.get_or_create(name='teacher')
            user.groups.add(group)
            login(request, user)
            messages.success(request, 'Teacher registration successful!')
            return redirect('teachers:dashboard')
    return render(request, 'registration/register_teacher.html')

def register_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            group, _ = Group.objects.get_or_create(name='student')
            user.groups.add(group)
            login(request, user)
            messages.success(request, 'Student registration successful!')
            return redirect('students:dashboard')
    return render(request, 'registration/register_student.html')
