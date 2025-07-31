from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from teachers.models import Quiz, Question
from students.models import StudentResponse, StudentFeedback

@login_required
def view_feedback(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    feedback = get_object_or_404(StudentFeedback, student=request.user, quiz=quiz)
    return render(request, 'feedback/view_feedback.html', {'feedback': feedback})

@login_required
def generate_feedback(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    responses = StudentResponse.objects.filter(student=request.user, quiz=quiz)
    
    # Calculate scores for each Bloom's level
    level_scores = {}
    level_counts = {}
    
    for response in responses:
        level = response.question.bloom_level
        if level not in level_counts:
            level_counts[level] = 0
            level_scores[level] = 0
        level_counts[level] += 1
        if response.is_correct:
            level_scores[level] += 1
    
    # Calculate percentages for each level
    feedback_data = {}
    overall_score = 0
    
    for level in level_counts:
        score = (level_scores[level] / level_counts[level]) * 100
        feedback_data[f"{level}_score"] = score
        overall_score += score
    
    overall_score = overall_score / len(level_counts) if level_counts else 0
    
    # Generate feedback text based on scores
    feedback_text = "Based on your quiz performance:\n\n"
    
    for level, score in feedback_data.items():
        level_name = level.replace('_score', '').capitalize()
        if score >= 80:
            feedback_text += f"✅ Excellent {level_name} level understanding ({score:.1f}%)\n"
        elif score >= 60:
            feedback_text += f"👍 Good {level_name} level understanding ({score:.1f}%)\n"
        else:
            feedback_text += f"❗ Need improvement in {level_name} level ({score:.1f}%)\n"
    
    # Save or update feedback
    feedback, created = StudentFeedback.objects.update_or_create(
        student=request.user,
        quiz=quiz,
        defaults={
            'remember_score': feedback_data.get('remember_score', 0),
            'understand_score': feedback_data.get('understand_score', 0),
            'apply_score': feedback_data.get('apply_score', 0),
            'analyze_score': feedback_data.get('analyze_score', 0),
            'evaluate_score': feedback_data.get('evaluate_score', 0),
            'create_score': feedback_data.get('create_score', 0),
            'overall_score': overall_score,
            'feedback_text': feedback_text
        }
    )
    
    return redirect('feedback:view_feedback', quiz_id=quiz.id)
