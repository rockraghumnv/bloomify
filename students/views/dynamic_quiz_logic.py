# In students/views/dynamic_quiz_logic.py

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

# --- Level-Specific Instructions for Better Question Quality ---
LEVEL_INSTRUCTIONS = {
    "remember": {
        "desc": "Ask the user to recall facts and basic concepts from the syllabus.",
        "format": "Options should be simple words or short phrases."
    },
    "understand": {
        "desc": "Ask the user to explain ideas or concepts. The user should need to interpret or summarize information.",
        "format": "Options should be sentences that explain a concept."
    },
    "apply": {
        "desc": "Ask the user to apply a concept from the syllabus to solve a problem. The question should present a scenario, and the options should be code snippets that solve it.",
        "format": "Options MUST be Python code snippets. For example: `A) if x > 5:\\n   print('Hello')`"
    },
    "analyze": {
        "desc": "Ask the user to analyze a piece of code or a scenario, breaking it down into its components to understand its structure or how it works.",
        "format": "The question should contain a code snippet, and the options should be analytical statements about that code."
    },
    "evaluate": {
        "desc": "Ask the user to evaluate two or more code snippets based on a criterion like efficiency, correctness, or style. The user must justify a choice.",
        "format": "Options MUST be different Python code snippets that achieve a similar goal, and the question will ask which is 'best' for a certain reason."
    },
    "create": {
        "desc": "Ask the user to identify the correct code structure or snippet required to build something new based on a set of requirements.",
        "format": "The question will describe a goal, and the options MUST be different Python code snippets that attempt to achieve that goal."
    }
}


# --- NEW, MORE ROBUST HELPER FUNCTION ---
def parse_question_from_response(response_text):
    """
    A more robust, line-by-line parser for the model's response.
    It correctly handles multi-line code snippets in options.
    """
    lines = response_text.strip().split('\n')
    
    question, topic, correct_letter = "", "", ""
    options = {}
    current_option_key = None
    buffer = []

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if stripped_line.lower().startswith("question:"):
            question = stripped_line[len("question:"):].strip()
        elif stripped_line.lower().startswith("topic:"):
            topic = stripped_line[len("topic:"):].strip()
        elif stripped_line.lower().startswith("correct:"):
            if current_option_key:  # Save the last option buffer before processing 'Correct:'
                options[current_option_key] = "\n".join(buffer).strip()
            correct_letter = stripped_line[len("correct:"):].strip().upper()
            current_option_key = None  # Stop capturing
        elif re.match(r'^[A-D]\)', stripped_line, re.IGNORECASE):
            if current_option_key:  # A new option is starting, so save the previous one
                options[current_option_key] = "\n".join(buffer).strip()
            
            current_option_key = stripped_line[0].upper()
            buffer = [stripped_line[2:].strip()]  # Start a new buffer for the new option
        elif current_option_key:  # If we are in the middle of capturing an option
            buffer.append(line) # Append the raw line to preserve indentation

    # Final check and format
    if question and len(options) == 4 and correct_letter in options:
        # Ensure options are always in A, B, C, D order
        ordered_options = [options.get('A', ''), options.get('B', ''), options.get('C', ''), options.get('D', '')]
        return {
            "question": question,
            "options": ordered_options,
            "correct_answer": options[correct_letter],
            "topic": topic or "General"
        }
    
    # If parsing fails, print the problematic response for debugging
    print("--- PARSING FAILED ---")
    print("Could not parse the following response from the AI:")
    print(response_text)
    print("----------------------")
    return None

def initialize_quiz_state(session):
    """Initializes or validates the quiz state in the user's session."""
    quiz_state = session.get('quiz_state', {})
    required_keys = ["level_index", "questions_answered_in_level", "asked_questions", "chat_history"]

    if not all(key in quiz_state for key in required_keys):
        system_instruction = "You are an expert educator and assessment designer..." # Full instruction
        quiz_state = {
            "level_index": 0,
            "questions_answered_in_level": 0,
            "correct_in_level": 0,
            "max_level_reached": 0,
            "asked_questions": [],
            "final_summary": [],
            "chat_history": [
                {'role': 'user', 'parts': [system_instruction]},
                {'role': 'model', 'parts': ["Understood."]}
            ]
        }
        session['quiz_state'] = quiz_state
    return quiz_state


def handle_dynamic_quiz(request):
    """Handles the dynamic quiz flow with intelligent, level-aware prompting."""
    teacher_id = request.session.get('quiz_teacher_id')
    syllabus_id = request.session.get('quiz_syllabus_id')
    if not (teacher_id and syllabus_id):
        messages.error(request, 'Quiz session expired. Please start again.')
        return redirect('students:dashboard')

    quiz_state = initialize_quiz_state(request.session)
    num_per_taxonomy = int(request.session.get('quiz_num_per_taxonomy', 3))

    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        current_question = request.session.get('current_question_data', {})
        
        is_correct = (user_answer.strip() == current_question.get('correct_answer').strip())
        if is_correct:
            quiz_state['correct_in_level'] += 1
        
        quiz_state['questions_answered_in_level'] += 1
        quiz_state['asked_questions'].append(current_question.get('question'))
        quiz_state['final_summary'].append({
            'level': BLOOM_LEVELS[quiz_state['level_index']],
            'question': current_question.get('question'),
            'topic': current_question.get('topic'),
            'is_correct': is_correct
        })

        if quiz_state['questions_answered_in_level'] >= num_per_taxonomy:
            pass_marks = {3: 2, 6: 4, 8: 6}
            required_to_pass = pass_marks.get(num_per_taxonomy, 2)

            if quiz_state['correct_in_level'] >= required_to_pass:
                quiz_state['level_index'] += 1
                if quiz_state['level_index'] > quiz_state['max_level_reached']:
                    quiz_state['max_level_reached'] = quiz_state['level_index']
            else:
                quiz_state['level_index'] -= 1
            
            quiz_state['correct_in_level'] = 0
            quiz_state['questions_answered_in_level'] = 0
        
        request.session['quiz_state'] = quiz_state
        return redirect('students:dynamic_quiz')

    level_index = quiz_state['level_index']

    if level_index < 0 or level_index >= len(BLOOM_LEVELS):
        reason = "Congratulations! You mastered all levels." if level_index >= len(BLOOM_LEVELS) else "Quiz ended."
        return render(request, 'students/quiz_complete_dynamic.html', {
            'summary': quiz_state['final_summary'],
            'reason': reason
        })
    
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, teacher_id=teacher_id)
    level_name = BLOOM_LEVELS[level_index]
    
    mcq = None
    for i in range(3): # Retry up to 3 times
        print(f"Attempt {i+1} to generate a unique question for level '{level_name}'...")
        
        level_instruction = LEVEL_INSTRUCTIONS[level_name]
        
        prompt = f"""
        Here is the entire course syllabus:
        ---
        {syllabus.content}
        ---
        Your task: {level_instruction['desc']}
        
        CRITICAL RULE: Do NOT repeat any of the following questions:
        ---
        {', '.join(quiz_state['asked_questions'])}
        ---
        
        Format your response STRICTLY as follows. {level_instruction['format']}
        Topic: [Name of the Module/Topic you chose]
        Question: [The question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct: [The correct letter, e.g., A]
        """
        
        chat_history = quiz_state['chat_history']
        chat_history.append({'role': 'user', 'parts': [prompt]})
        
        try:
            response = MODEL.generate_content(chat_history)
            chat_history.append({'role': 'model', 'parts': [response.text]})
            
            parsed_mcq = parse_question_from_response(response.text)

            if parsed_mcq and parsed_mcq.get('question') not in quiz_state['asked_questions']:
                mcq = parsed_mcq
                break
                
        except Exception as e:
            print(f"An API error occurred during generation: {e}")
            continue

    quiz_state['chat_history'] = chat_history

    if not mcq:
        messages.error(request, "Failed to generate a unique question. The quiz has been reset.")
        request.session.pop('quiz_state', None)
        return redirect('students:dashboard')

    request.session['current_question_data'] = mcq
    request.session['quiz_state'] = quiz_state
    
    return render(request, 'students/dynamic_quiz.html', {
        'question_data': mcq,
        'level_name': level_name.capitalize(),
        'current_q_num': quiz_state['questions_answered_in_level'] + 1,
        'total_q_in_level': num_per_taxonomy
    })
