# In students/views/descriptive_quiz_logic.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from teachers.models import Syllabus
import google.generativeai as genai
from django.conf import settings
import re

# --- Configuration ---
genai.configure(api_key=settings.API_KEY)
MODEL = genai.GenerativeModel('gemini-1.5-flash')
BLOOM_LEVELS = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']

# --- NEW: Level-Specific Instructions for Descriptive Questions ---
LEVEL_INSTRUCTIONS_DESCRIPTIVE = {
    "remember": "Generate a direct, factual question that requires recalling a definition or term from the syllabus. Also, provide a comma-separated list of 3-4 essential keywords a correct answer must contain.",
    "understand": "Generate a question that requires the user to explain a concept in their own words. Provide a comma-separated list of 4-5 keywords that a good explanation would include in sequence.",
    "apply": "Generate a question that presents a simple problem scenario and asks how a specific concept from the syllabus would be used to solve it. Provide a comma-separated list of 5-6 keywords, in order, that would appear in a correct procedural answer.",
    "analyze": "Generate a question that requires the user to break down a concept into its constituent parts or compare and contrast two concepts from the syllabus. Provide a comma-separated list of 5-6 important keywords, in order, that a correct analysis should contain.",
    "evaluate": "Generate a question that asks the user to make a judgment or critique a concept from the syllabus, based on a given criterion (e.g., 'What is the main advantage of...?'). Provide a comma-separated list of 5-7 keywords, in order, that a well-reasoned evaluation would include.",
    "create": "Generate a question that asks the user to propose a plan or design a simple concept based on the principles in the syllabus (e.g., 'Outline the steps to create...'). Provide a comma-separated list of 6-8 keywords, in order, that a comprehensive plan would cover."
}

# --- Helper Functions ---
def parse_descriptive_response(response_text):
    """Parses a descriptive question and its evaluation keywords from the AI's response."""
    lines = response_text.strip().split('\n')
    question, keywords_str = "", ""
    for line in lines:
        if line.lower().startswith("question:"):
            question = line[len("question:"):].strip()
        elif line.lower().startswith("keywords:"):
            keywords_str = line[len("keywords:"):].strip()
    
    if question and keywords_str:
        keywords = [k.strip().lower() for k in keywords_str.split(',')]
        return {"question": question, "keywords": keywords}
    
    print(f"--- PARSING FAILED (Descriptive) ---\n{response_text}\n----------------------")
    return None

def evaluate_answer_with_lcs(student_answer, ai_keywords):
    """
    Evaluates the student's answer by finding the Longest Common Subsequence (LCS)
    of keywords, which respects order.
    """
    if not student_answer or not ai_keywords:
        return 0.0

    student_words = [word.strip(".,!?").lower() for word in student_answer.split()]
    
    m, n = len(ai_keywords), len(student_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ai_keywords[i-1] == student_words[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    lcs_length = dp[m][n]
    match_percentage = (lcs_length / len(ai_keywords)) * 100
    
    print(f"LCS Match: {lcs_length}/{len(ai_keywords)} keywords = {match_percentage:.2f}%")
    return match_percentage

def initialize_quiz_state(session):
    if 'desc_quiz_state' not in session:
        system_instruction = "You are an expert educator who creates descriptive questions and evaluation keywords based on a syllabus."
        session['desc_quiz_state'] = {
            "level_index": 0,
            "questions_answered_in_level": 0,
            "correct_in_level": 0,
            "max_level_reached": 0,
            "asked_questions": {str(i): [] for i in range(len(BLOOM_LEVELS))},
            "final_summary": [],
            "chat_history": [{'role': 'user', 'parts': [system_instruction]}, {'role': 'model', 'parts': ["Understood."]}]
        }
    return session['desc_quiz_state']

# --- Main View Logic ---
def handle_descriptive_quiz(request):
    teacher_id = request.session.get('quiz_teacher_id')
    syllabus_id = request.session.get('quiz_syllabus_id')
    if not (teacher_id and syllabus_id):
        messages.error(request, 'Quiz session expired. Please start again.')
        return redirect('students:dashboard')

    quiz_state = initialize_quiz_state(request.session)
    num_per_taxonomy = int(request.session.get('quiz_num_per_taxonomy', 3))

    if request.method == 'POST':
        student_answer = request.POST.get('student_answer', '')
        current_question = request.session.get('current_question_data', {})
        level_index_str = str(quiz_state['level_index'])
        
        match_score = evaluate_answer_with_lcs(student_answer, current_question.get('keywords', []))
        is_correct = match_score >= 70.0

        if is_correct:
            quiz_state['correct_in_level'] += 1
        
        quiz_state['questions_answered_in_level'] += 1
        quiz_state['asked_questions'][level_index_str].append(current_question.get('question'))
        quiz_state['final_summary'].append({
            'level': BLOOM_LEVELS[quiz_state['level_index']],
            'question': current_question.get('question'),
            'student_answer': student_answer,
            'match_score': f"{match_score:.1f}%",
            'is_correct': is_correct
        })

        if quiz_state['questions_answered_in_level'] >= num_per_taxonomy:
            required_to_pass = 2
            if quiz_state['correct_in_level'] >= required_to_pass:
                quiz_state['level_index'] += 1
                if quiz_state['level_index'] > quiz_state['max_level_reached']:
                    quiz_state['max_level_reached'] = quiz_state['level_index']
            else:
                quiz_state['level_index'] -= 1
            
            quiz_state['correct_in_level'] = 0
            quiz_state['questions_answered_in_level'] = 0
        
        request.session['desc_quiz_state'] = quiz_state
        return redirect('students:descriptive_quiz')

    level_index = quiz_state['level_index']

    if level_index < 0 or level_index >= len(BLOOM_LEVELS):
        reason = "Congratulations!" if level_index >= len(BLOOM_LEVELS) else "Quiz ended."
        return render(request, 'students/quiz_complete_descriptive.html', {
            'summary': quiz_state['final_summary'], 'reason': reason
        })
    
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, teacher_id=teacher_id)
    level_name = BLOOM_LEVELS[level_index]
    
    descriptive_question = None
    for _ in range(3):
        instruction = LEVEL_INSTRUCTIONS_DESCRIPTIVE[level_name]
        already_asked = quiz_state['asked_questions'].get(str(level_index), [])
        
        prompt = f"Syllabus Content:\n---\n{syllabus.content}\n---\nTask: {instruction}\nCRITICAL: Do not repeat these questions: {', '.join(already_asked)}\nFormat your response STRICTLY as:\nQuestion: [Your question here]\nKeywords: [keyword1, keyword2, keyword3, ...]"
        
        chat_history = quiz_state['chat_history']
        chat_history.append({'role': 'user', 'parts': [prompt]})
        
        try:
            response = MODEL.generate_content(chat_history)
            chat_history.append({'role': 'model', 'parts': [response.text]})
            parsed_question = parse_descriptive_response(response.text)
            if parsed_question and parsed_question.get('question') not in already_asked:
                descriptive_question = parsed_question
                break
        except Exception as e:
            print(f"API Error: {e}")

    quiz_state['chat_history'] = chat_history

    if not descriptive_question:
        messages.error(request, "Failed to generate a question. Please try again.")
        request.session.pop('desc_quiz_state', None)
        return redirect('students:dashboard')

    request.session['current_question_data'] = descriptive_question
    request.session['desc_quiz_state'] = quiz_state
    
    return render(request, 'students/descriptive_quiz.html', {
        'question_data': descriptive_question,
        'level_name': level_name.capitalize(),
        'current_q_num': quiz_state['questions_answered_in_level'] + 1,
        'total_q_in_level': num_per_taxonomy
    })
