from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from teachers.models import Syllabus
import google.generativeai as genai
from django.conf import settings
import re

# Helper to split syllabus into modules
MODULE_SPLIT_REGEX = r"(?:^|\n)(Module|Unit|Chapter)\s*\d+[:\-. ]*"

def split_syllabus_modules(syllabus_text):
    # Find all module/unit/chapter headers and split
    matches = list(re.finditer(MODULE_SPLIT_REGEX, syllabus_text, re.IGNORECASE))
    modules = []
    if not matches:
        return [syllabus_text] if syllabus_text.strip() else []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(syllabus_text)
        modules.append(syllabus_text[start:end].strip())
    return [m for m in modules if m]

# ...existing code...

def split_syllabus_modules(syllabus_text):
    matches = list(re.finditer(MODULE_SPLIT_REGEX, syllabus_text, re.IGNORECASE))
    modules = []
    if not matches:
        return [syllabus_text] if syllabus_text.strip() else []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(syllabus_text)
        modules.append(syllabus_text[start:end].strip())
    return [m for m in modules if m]

def handle_dynamic_quiz(request):
    teacher_id = request.session.get('quiz_teacher_id')
    syllabus_id = request.session.get('quiz_syllabus_id')
    num_per_taxonomy = int(request.session.get('quiz_num_per_taxonomy', 3))
    progress = request.session.get('quiz_progress', {
        'taxonomy_index': 0,
        'current_count': 0,
        'correct_in_level': 0,
        'wrong_in_level': 0,
        'history': [],
        'asked_questions': {},
    })
    bloom_levels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
    taxonomy_index = progress['taxonomy_index']
    current_count = progress['current_count']
    correct_in_level = progress['correct_in_level']
    wrong_in_level = progress['wrong_in_level']
    history = progress['history']
    asked_questions = progress.get('asked_questions', {})

    if not (teacher_id and syllabus_id):
        messages.error(request, 'Quiz session not found. Please start again.')
        return redirect('students:dashboard')

    syllabus = get_object_or_404(Syllabus, id=syllabus_id, teacher_id=teacher_id)
    syllabus_text = syllabus.content or ''
    modules = split_syllabus_modules(syllabus_text)
    if not modules:
        modules = [syllabus_text] if syllabus_text.strip() else []

    pass_marks = {3: 2, 6: 5, 8: 7}
    required_correct = pass_marks.get(num_per_taxonomy, 2)

    if request.method == 'POST':
        answer = request.POST.get('answer')
        correct_answer = request.session.get('current_correct_answer')
        question_text = request.session.get('current_question_text')
        options = request.session.get('current_options')
        is_correct = (answer == correct_answer)
        history.append({
            'taxonomy': bloom_levels[taxonomy_index],
            'question': question_text,
            'selected': answer,
            'correct': correct_answer,
            'is_correct': is_correct,
            'options': options
        })
        asked_questions.setdefault(str(taxonomy_index), [])
        asked_questions[str(taxonomy_index)].append(question_text)
        if is_correct:
            correct_in_level += 1
        else:
            wrong_in_level += 1
        current_count += 1
        if current_count >= num_per_taxonomy:
            if correct_in_level >= required_correct:
                taxonomy_index += 1
                current_count = 0
                correct_in_level = 0
                wrong_in_level = 0
                if taxonomy_index >= len(bloom_levels):
                    request.session['quiz_progress'] = {
                        'taxonomy_index': taxonomy_index,
                        'current_count': current_count,
                        'correct_in_level': correct_in_level,
                        'wrong_in_level': wrong_in_level,
                        'history': history,
                        'asked_questions': asked_questions
                    }
                    return render(request, 'students/quiz_complete_dynamic.html', {
                        'history': history,
                        'ended_on': 'Completed all levels',
                        'reason': 'Congratulations! You completed all taxonomy levels.'
                    })
            else:
                request.session['quiz_progress'] = {
                    'taxonomy_index': taxonomy_index,
                    'current_count': current_count,
                    'correct_in_level': correct_in_level,
                    'wrong_in_level': wrong_in_level,
                    'history': history,
                    'asked_questions': asked_questions
                }
                return render(request, 'students/quiz_complete_dynamic.html', {
                    'history': history,
                    'ended_on': bloom_levels[taxonomy_index],
                    'reason': f'You needed {required_correct} correct answers to pass this taxonomy. Quiz ended.'
                })
        request.session['quiz_progress'] = {
            'taxonomy_index': taxonomy_index,
            'current_count': current_count,
            'correct_in_level': correct_in_level,
            'wrong_in_level': wrong_in_level,
            'history': history,
            'asked_questions': asked_questions
        }

    num_modules = len(modules)
    questions_per_taxonomy = num_per_taxonomy
    if num_modules == 0:
        module_question_counts = [questions_per_taxonomy]
    else:
        base = questions_per_taxonomy // num_modules
        extra = questions_per_taxonomy % num_modules
        module_question_counts = [base + (1 if i < extra else 0) for i in range(num_modules)]

    module_question_indices = progress.get('module_question_indices', [0]*num_modules)
    module_index = 0
    for i, count in enumerate(module_question_counts):
        if module_question_indices[i] < count:
            module_index = i
            break
    else:
        module_index = 0

    level = bloom_levels[taxonomy_index]
    bloom_instructions = {
        'remember': {
            'desc': 'Recall facts, terms, basic concepts, or answers. Use verbs like define, list, recall, name, identify.',
            'example': 'Question: What is the output of print(2 + 2) in Python?\nA) 22\nB) 4\nC) 2+2\nD) Error\nCorrect: B'
        },
        'understand': {
            'desc': 'Demonstrate understanding of facts and ideas by organizing, comparing, interpreting, giving descriptions, and stating main ideas. Use verbs like explain, summarize, interpret, classify.',
            'example': 'Question: Which statement best explains the purpose of a function in Python?\nA) To store data\nB) To repeat code\nC) To group code for reuse\nD) To create variables\nCorrect: C'
        },
        'apply': {
            'desc': 'Use information in new situations. Use verbs like use, solve, demonstrate, implement, execute.',
            'example': 'Question: Which code will output "Hello" in Python?\nA) echo "Hello"\nB) print("Hello")\nC) printf("Hello")\nD) cout << "Hello"\nCorrect: B'
        },
        'analyze': {
            'desc': 'Draw connections among ideas, break information into parts, and examine relationships. Use verbs like analyze, differentiate, compare, contrast, examine.',
            'example': 'Question: Which part of the following code is the function definition? def add(a, b): return a + b\nA) add(a, b)\nB) def add(a, b):\nC) return a + b\nD) a, b\nCorrect: B'
        },
        'evaluate': {
            'desc': 'Justify a decision or course of action. Use verbs like evaluate, justify, critique, recommend, assess.',
            'example': 'Question: Which code is the most efficient way to iterate over a list in Python?\nA) Using a while loop\nB) Using a for loop\nC) Using recursion\nD) Using goto\nCorrect: B'
        },
        'create': {
            'desc': 'Produce new or original work. Use verbs like design, construct, develop, formulate, author.',
            'example': 'Question: Which code defines a new class in Python?\nA) def MyClass:\nB) class MyClass:\nC) create MyClass()\nD) function MyClass()\nCorrect: B'
        },
    }
    instructions = bloom_instructions[level]
    all_asked = set()
    for qlist in asked_questions.values():
        all_asked.update(qlist)
    for _ in range(5):
        prompt = f"""
You are an expert educator and assessment designer. Your task is to generate 1 high-quality multiple choice question (MCQ) that strictly assesses the {level.upper()} level of Bloom's Taxonomy for the following module content (from a syllabus):
---
{modules[module_index][:2000]}
---
Guidelines:
- The question must target ONLY the {level.upper()} cognitive level. Do NOT mix levels.
- Use cognitive verbs and skills for {level.upper()}: {instructions['desc']}
- Make the question relevant to the module and avoid trivia.
- The question must have 4 plausible options (A, B, C, D) and only one correct answer.
- Each option must be a short phrase or sentence, not a code block or blank.
- Do NOT ask for code writing or open-ended answers. Only MCQ format.
- Avoid ambiguous or trick questions.
- Use clear, concise language suitable for the subject.
- Do NOT repeat questions or options that have already been asked: {', '.join(all_asked)}
Format:
Question: [question text]
A) [option1]
B) [option2]
C) [option3]
D) [option4]
Correct: [A/B/C/D]
Example for {level.upper()}:
{instructions['example']}
Generate the question in the above format only. Do NOT ask for code writing or open-ended answers.
"""
        api_key = settings.API_KEY
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        questions_text = response.text.strip()
        lines = [l.strip() for l in questions_text.split('\n') if l.strip()]
        question_text = ''
        options = []
        correct_answer = ''
        for line in lines:
            if line.startswith('Question:'):
                question_text = line.replace('Question:', '').strip()
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_val = line.split(')', 1)[1].strip()
                if option_val and not option_val.startswith('```'):
                    options.append(option_val)
            elif line.startswith('Correct:'):
                correct_letter = line.replace('Correct:', '').strip()
                answer_map = {'A': options[0] if len(options)>0 else '', 'B': options[1] if len(options)>1 else '', 'C': options[2] if len(options)>2 else '', 'D': options[3] if len(options)>3 else ''}
                correct_answer = answer_map.get(correct_letter, '')
        if question_text and question_text not in all_asked and len(options) == 4 and all(options):
            break
    module_question_indices[module_index] += 1
    progress['module_question_indices'] = module_question_indices
    request.session['current_question_text'] = question_text
    request.session['current_options'] = options
    request.session['current_correct_answer'] = correct_answer
    request.session['quiz_progress'] = progress
    return render(request, 'students/dynamic_quiz.html', {
        'question_text': question_text,
        'options': options,
        'taxonomy': level,
        'current_count': current_count + 1,
        'num_per_taxonomy': num_per_taxonomy,
        'taxonomy_label': level.capitalize(),
        'progress': progress
    })
