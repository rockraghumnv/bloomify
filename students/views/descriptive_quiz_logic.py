# In students/views/descriptive_quiz_logic.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from teachers.models import Syllabus
import google.generativeai as genai
from django.conf import settings
import re
import random

# --- Configuration ---
genai.configure(api_key=settings.API_KEY)
MODEL = genai.GenerativeModel('gemini-2.5-flash')
BLOOM_LEVELS = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']

# --- NEW: Level-Specific Instructions for Descriptive Questions ---
LEVEL_INSTRUCTIONS_DESCRIPTIVE = {
    "remember": """
    REMEMBER LEVEL: Generate questions that test ONLY basic recall of facts, definitions, or simple information.
    - Ask ONLY for definitions, facts, lists, or identification
    - Use verbs like: define, list, identify, state, name, recall, what is, who is
    - NO explanations, scenarios, applications, or complex thinking required
    - The answer should be a simple fact or definition
    
    EXAMPLES of CORRECT Remember questions:
    - "What is a Python variable?"
    - "Define a Python function"
    - "List the basic data types in Python"
    - "What is the syntax for a Python if statement?"
    
    EXAMPLES of INCORRECT questions for Remember (these are higher levels):
    - "Explain how Python functions work" (Understanding)
    - "How would you use a function to solve this problem?" (Apply)
    - "Compare lists and tuples" (Analyze)
    """,
    
    "understand": """
    UNDERSTAND LEVEL: Generate questions that test comprehension and explanation of concepts.
    - Ask for explanations, descriptions, or how things work
    - Use verbs like: explain, describe, discuss, summarize, interpret
    - The answer should demonstrate understanding, not just recall
    - Focus on comprehension of processes, concepts, or relationships
    
    EXAMPLES of CORRECT Understand questions:
    - "Explain how Python functions work"
    - "Describe the difference between lists and tuples"
    - "Discuss how loops control program flow"
    
    EXAMPLES of INCORRECT questions for Understand:
    - "What is a Python function?" (Remember)
    - "How would you use a function in this scenario?" (Apply)
    """,
    
    "apply": """
    APPLY LEVEL: Generate questions that test the ability to use knowledge in new situations.
    - Present a specific scenario or problem to solve
    - Ask how to use concepts in practical situations
    - Use verbs like: apply, use, implement, solve, demonstrate, show how
    - The answer should show practical application of knowledge
    
    EXAMPLES of CORRECT Apply questions:
    - "How would you use a Python function to calculate the average of student grades?"
    - "You need to store user information - which data structure would you use and how?"
    - "Demonstrate how to use a loop to process a list of numbers"
    
    EXAMPLES of INCORRECT questions for Apply:
    - "What is a Python function?" (Remember)
    - "Explain how functions work" (Understand)
    """,
    
    "analyze": """
    ANALYZE LEVEL: Generate questions that test the ability to break down concepts and examine relationships.
    - Ask to compare, contrast, differentiate, or examine parts
    - Use verbs like: analyze, compare, contrast, examine, differentiate, break down
    - The answer should show analysis of components or relationships
    - Focus on examining how parts relate to the whole
    
    EXAMPLES of CORRECT Analyze questions:
    - "Compare the advantages and disadvantages of lists vs dictionaries"
    - "Analyze when you would use a for loop vs a while loop"
    - "Examine the differences between functions and methods"
    
    EXAMPLES of INCORRECT questions for Analyze:
    - "What is a list?" (Remember)
    - "How would you use a list?" (Apply)
    """,
    
    "evaluate": """
    EVALUATE LEVEL: Generate questions that test the ability to make judgments and assess value.
    - Ask for judgments, assessments, or evaluations with justification
    - Use verbs like: evaluate, assess, judge, critique, justify, recommend
    - The answer should include judgment and reasoning
    - Focus on making informed decisions or assessments
    
    EXAMPLES of CORRECT Evaluate questions:
    - "Evaluate which sorting algorithm would be best for this dataset and justify your choice"
    - "Assess the effectiveness of using functions vs inline code for this program"
    - "Judge whether using a dictionary or list is better for this scenario and explain why"
    
    EXAMPLES of INCORRECT questions for Evaluate:
    - "What is a sorting algorithm?" (Remember)
    - "How do you implement a sort?" (Apply)
    """,
    
    "create": """
    CREATE LEVEL: Generate questions that test the ability to create, design, or build new solutions.
    - Ask to design, create, build, or propose new solutions
    - Use verbs like: create, design, develop, build, construct, propose, plan
    - The answer should involve creating something new or original
    - Focus on combining elements to form new solutions
    
    EXAMPLES of CORRECT Create questions:
    - "Design a program structure for a student management system"
    - "Create a plan for organizing a large Python project into modules"
    - "Develop a strategy for handling errors in a web application"
    
    EXAMPLES of INCORRECT questions for Create:
    - "What is program structure?" (Remember)
    - "How do you use modules?" (Apply)
    """
}

# --- Helper Functions ---
def normalize_keyword(keyword):
    """
    Normalize keywords by handling hyphens, underscores, and common variations.
    """
    if not keyword:
        return keyword
    
    # Convert to lowercase and handle compound words
    normalized = keyword.lower()
    # Replace hyphens and underscores with spaces for matching
    normalized = re.sub(r'[-_]', ' ', normalized)
    return normalized.strip()

def get_keyword_synonyms(keyword):
    """
    Get synonyms and variations for common technical keywords.
    """
    synonym_map = {
        # Programming concepts
        'function': ['function', 'func', 'method', 'procedure'],
        'variable': ['variable', 'var', 'identifier', 'name'],
        'loop': ['loop', 'iteration', 'iterate', 'repeat'],
        'condition': ['condition', 'conditional', 'test', 'check'],
        'boolean': ['boolean', 'bool', 'true/false', 'logical'],
        'string': ['string', 'str', 'text', 'character'],
        'integer': ['integer', 'int', 'number', 'whole number'],
        'float': ['float', 'decimal', 'floating point', 'real number'],
        
        # Operations and methods
        'append': ['append', 'add', 'insert', 'push'],
        'remove': ['remove', 'delete', 'pop', 'eliminate'],
        'equality': ['equality', 'equal', 'equals', 'same'],
        'inequality': ['inequality', 'not equal', 'different', 'unequal'],
        'comparison': ['comparison', 'compare', 'comparing', 'contrast'],
        
        # Data structures
        'list': ['list', 'array', 'sequence', 'collection'],
        'tuple': ['tuple', 'immutable sequence'],
        'dictionary': ['dictionary', 'dict', 'map', 'hash table'],
        
        # File operations
        'read': ['read', 'reading', 'input', 'load'],
        'write': ['write', 'writing', 'output', 'save'],
        'append': ['append', 'add to end', 'attach'],
        
        # Control flow
        'while loop': ['while', 'while loop', 'conditional loop'],
        'for loop': ['for', 'for loop', 'iteration loop'],
        'if statement': ['if', 'if statement', 'conditional'],
        
        # Modules and imports
        'import': ['import', 'importing', 'include', 'load'],
        'module': ['module', 'library', 'package', 'file'],
        'functionality': ['functionality', 'features', 'capabilities', 'functions'],
        'extension': ['extension', 'expand', 'enhance', 'add to'],
        
        # Object-oriented concepts
        'class': ['class', 'object type', 'template'],
        'object': ['object', 'instance', 'entity'],
        'method': ['method', 'function', 'operation'],
        'attribute': ['attribute', 'property', 'field', 'variable'],
        
        # Common programming terms
        'parameter': ['parameter', 'argument', 'input', 'param'],
        'argument': ['argument', 'parameter', 'value', 'input'],
        'return': ['return', 'output', 'result', 'give back'],
        'syntax': ['syntax', 'format', 'structure', 'grammar'],
        'error': ['error', 'exception', 'mistake', 'problem'],
    }
    
    # Normalize the keyword first
    normalized_key = normalize_keyword(keyword)
    
    # Check for exact matches and partial matches
    for key, synonyms in synonym_map.items():
        if normalized_key == key or normalized_key in synonyms:
            return synonyms
        # Also check if any synonym contains the keyword or vice versa
        for synonym in synonyms:
            if normalized_key in synonym or synonym in normalized_key:
                return synonyms
    
    return [normalized_key]

def tokenize_text(text):
    """
    Enhanced tokenization that extracts meaningful tokens from text.
    """
    if not text:
        return []
    
    # Convert to lowercase and remove basic punctuation
    text = text.lower()
    # Remove common punctuation but keep word boundaries
    text = re.sub(r'[^\w\s-]', ' ', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text).strip()
    # Split into words
    words = text.split()
    
    # Comprehensive stopwords list
    stopwords_list = {
        # Articles and determiners
        'a', 'an', 'the', 'this', 'that', 'these', 'those', 'some', 'any', 'each', 'every',
        # Prepositions
        'at', 'by', 'for', 'from', 'in', 'of', 'on', 'to', 'with', 'into', 'onto', 'upon',
        'over', 'under', 'above', 'below', 'through', 'during', 'before', 'after', 'between',
        'among', 'within', 'without', 'beyond', 'toward', 'towards', 'across', 'against',
        # Pronouns
        'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
        'we', 'us', 'our', 'ours', 'ourselves', 'they', 'them', 'their', 'theirs', 'themselves',
        # Conjunctions
        'and', 'or', 'but', 'so', 'yet', 'nor', 'although', 'though', 'because', 'since',
        'while', 'whereas', 'if', 'unless', 'until', 'when', 'where', 'how', 'why', 'what',
        # Auxiliary verbs and common verbs
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
        'do', 'does', 'did', 'doing', 'will', 'would', 'shall', 'should', 'can', 'could',
        'may', 'might', 'must', 'ought', 'need', 'dare', 'used',
        # Common adverbs
        'not', 'no', 'yes', 'very', 'too', 'quite', 'rather', 'really', 'just', 'only',
        'also', 'even', 'still', 'already', 'yet', 'again', 'once', 'twice', 'here', 'there',
        'where', 'everywhere', 'somewhere', 'anywhere', 'nowhere', 'then', 'now', 'today',
        'yesterday', 'tomorrow', 'always', 'never', 'sometimes', 'often', 'usually',
        # Question words and fillers
        'who', 'whom', 'whose', 'which', 'what', 'when', 'where', 'why', 'how', 'well',
        'sure', 'okay', 'right', 'left', 'good', 'bad', 'better', 'best', 'worse', 'worst',
        # Common phrases starters
        'let', 'lets', 'make', 'take', 'give', 'put', 'get', 'got', 'come', 'go', 'see', 'look',
        'know', 'think', 'feel', 'want', 'like', 'need', 'try', 'use', 'work', 'help',
        # Breakdown/explanation words
        'breakdown', 'explanation', 'difference', 'clear', 'understand', 'question'
    }
    
    # Filter out stopwords and short words, and remove duplicates while preserving order
    seen = set()
    tokens = []
    for word in words:
        if len(word) > 2 and word not in stopwords_list and word not in seen:
            tokens.append(word)
            seen.add(word)
    
    return tokens

def parse_descriptive_response(response_text):
    """Parses a descriptive question and its evaluation keywords from the AI's response."""
    lines = response_text.strip().split('\n')
    question, keywords_str, topic = "", "", ""
    
    for line in lines:
        line = line.strip()
        if line.lower().startswith("topic:"):
            topic = line[len("topic:"):].strip()
        elif line.lower().startswith("question:"):
            question = line[len("question:"):].strip()
        elif line.lower().startswith("keywords:"):
            keywords_str = line[len("keywords:"):].strip()
    
    if question and keywords_str:
        # Tokenize keywords and remove duplicates while preserving order
        raw_keywords = [k.strip().lower() for k in keywords_str.split(',')]
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in raw_keywords:
            if keyword and keyword not in seen and len(keyword) > 2:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        # Further process keywords to remove stopwords
        final_keywords = tokenize_text(' '.join(unique_keywords))
        
        return {
            "question": question, 
            "keywords": final_keywords,
            "topic": topic if topic else "General"
        }
    
    print(f"--- PARSING FAILED (Descriptive) ---\n{response_text}\n----------------------")
    return None

def evaluate_answer_with_token_sequence(student_answer, ai_keywords):
    """
    Enhanced evaluation that checks for token sequence matching with flexible synonym and phrase matching.
    Returns both score and detailed matching information for feedback storage.
    """
    if not student_answer or not ai_keywords:
        return 0.0, {}

    # Tokenize student answer
    student_tokens = tokenize_text(student_answer)
    
    if not student_tokens or not ai_keywords:
        return 0.0, {}
    
    print(f"AI Keywords: {ai_keywords}")
    print(f"Student Tokens (first 15): {student_tokens[:15]}")
    
    # Enhanced matching with synonyms and flexible phrase matching
    matches = 0
    total_possible = len(ai_keywords)
    matched_keywords = []
    unmatched_keywords = []
    
    # Create a normalized version of student text for phrase matching
    student_text_normalized = normalize_keyword(student_answer)
    
    for keyword in ai_keywords:
        found = False
        best_match = ""
        match_score = 0
        
        # Get synonyms for the keyword
        keyword_synonyms = get_keyword_synonyms(keyword)
        normalized_keyword = normalize_keyword(keyword)
        
        # Method 1: Check for phrase matches in normalized text
        for synonym in keyword_synonyms:
            normalized_synonym = normalize_keyword(synonym)
            if normalized_synonym in student_text_normalized:
                found = True
                best_match = synonym
                match_score = 1.0
                break
        
        # Method 2: Check individual tokens if no phrase match found
        if not found:
            for token in student_tokens:
                # Direct synonym matching
                if token in keyword_synonyms:
                    found = True
                    best_match = token
                    match_score = 1.0
                    break
                
                # Partial matching for longer words (stem matching)
                for synonym in keyword_synonyms:
                    if len(synonym) > 3 and len(token) > 3:
                        # Check if one contains the other (at least 4 characters)
                        if (synonym in token and len(synonym) >= 4) or (token in synonym and len(token) >= 4):
                            found = True
                            best_match = token
                            match_score = 0.8  # Slightly lower score for partial matches
                            break
                
                if found:
                    break
        
        # Method 3: Fuzzy matching for close spellings (basic)
        if not found:
            for token in student_tokens:
                if len(token) > 4 and len(normalized_keyword) > 4:
                    # Simple character overlap check
                    common_chars = set(token) & set(normalized_keyword)
                    if len(common_chars) >= min(len(token), len(normalized_keyword)) * 0.6:
                        found = True
                        best_match = token
                        match_score = 0.6  # Lower score for fuzzy matches
                        break
        
        if found:
            matches += match_score
            matched_keywords.append(f"{keyword}→{best_match}")
        else:
            unmatched_keywords.append(keyword)
    
    # Calculate final score with bonus for comprehensive coverage
    base_score = (matches / total_possible) * 100 if total_possible > 0 else 0
    
    # Bonus scoring system
    coverage_ratio = matches / total_possible if total_possible > 0 else 0
    if coverage_ratio >= 0.8:  # 80% or more keywords matched
        base_score *= 1.1  # 10% bonus
    elif coverage_ratio >= 0.6:  # 60-79% keywords matched
        base_score *= 1.05  # 5% bonus
    
    # Cap the score at 100%
    final_score = min(base_score, 100.0)
    
    print(f"Enhanced Evaluation Results:")
    print(f"  Matched: {matches}/{total_possible} ({coverage_ratio:.1%})")
    print(f"  Final Score: {final_score:.1f}%")
    print(f"  Matches: {matched_keywords}")
    if unmatched_keywords:
        print(f"  Unmatched: {unmatched_keywords}")
    
    # Return detailed results for storage
    evaluation_details = {
        'matched_count': matches,
        'total_keywords': total_possible,
        'coverage_ratio': coverage_ratio,
        'matched_keywords': matched_keywords,
        'unmatched_keywords': unmatched_keywords,
        'final_score': final_score
    }
    
    return final_score, evaluation_details

def initialize_quiz_state(session):
    if 'desc_quiz_state' not in session:
        system_instruction = "You are an expert educator who creates descriptive questions and evaluation keywords based on a syllabus."
        session['desc_quiz_state'] = {
            "level_index": 0,
            "questions_answered_in_level": 0,
            "correct_in_level": 0,
            "max_level_reached": 0,
            "asked_questions": [],  # Changed to simple list like MCQ
            "asked_topics": [],     # Added to track topics
            "final_summary": [],
            "session_id": f"desc_{random.randint(1000, 9999)}",  # Added session ID
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
        
        print(f"=== PROCESSING ANSWER ===")
        print(f"Student answer length: {len(student_answer)}")
        print(f"Current question exists: {'question' in current_question}")
        print(f"Level index: {quiz_state['level_index']}")
        print(f"Questions answered in level: {quiz_state['questions_answered_in_level']}")
        
        match_score, matching_details = evaluate_answer_with_token_sequence(student_answer, current_question.get('keywords', []))
        is_correct = match_score >= 70.0

        if is_correct:
            quiz_state['correct_in_level'] += 1
        
        quiz_state['questions_answered_in_level'] += 1
        quiz_state['asked_questions'].append(current_question.get('question', 'N/A'))  # Add fallback for N/A
        
        # Store detailed results for feedback system
        detailed_result = {
            'level': BLOOM_LEVELS[quiz_state['level_index']],
            'question': current_question.get('question', 'Question not available'),
            'student_answer': student_answer,
            'expected_keywords': current_question.get('keywords', []),
            'matched_keywords': matching_details,
            'match_score': f"{match_score:.1f}%",
            'score_percentage': match_score,
            'is_correct': is_correct,
            'topic': current_question.get('topic', 'General')
        }
        
        quiz_state['final_summary'].append(detailed_result)
        
        print(f"Added result to summary. Total questions: {len(quiz_state['final_summary'])}")

        if quiz_state['questions_answered_in_level'] >= num_per_taxonomy:
            required_to_pass = 2
            if quiz_state['correct_in_level'] >= required_to_pass:
                quiz_state['level_index'] += 1
                if quiz_state['level_index'] > quiz_state['max_level_reached']:
                    quiz_state['max_level_reached'] = quiz_state['level_index']
                print(f"PASSED level. Moving to level {quiz_state['level_index']}")
            else:
                quiz_state['level_index'] -= 1
                print(f"FAILED level. Moving to level {quiz_state['level_index']}")
                # If we go below level 0, end the quiz
                if quiz_state['level_index'] < 0:
                    print("Quiz ending due to failure at basic level")
            
            quiz_state['correct_in_level'] = 0
            quiz_state['questions_answered_in_level'] = 0
        
        request.session['desc_quiz_state'] = quiz_state
        return redirect('students:descriptive_quiz')

    level_index = quiz_state['level_index']
    total_questions_answered = len(quiz_state.get('final_summary', []))
    max_total_questions = num_per_taxonomy * len(BLOOM_LEVELS)  # Maximum possible questions

    # Safety mechanism: End quiz if too many questions have been answered
    if total_questions_answered >= max_total_questions:
        print(f"=== QUIZ ENDING: Maximum questions reached ({total_questions_answered}) ===")
        level_index = len(BLOOM_LEVELS)  # Force completion

    if level_index < 0 or level_index >= len(BLOOM_LEVELS):
        # Quiz is complete, save feedback and redirect
        print(f"=== QUIZ COMPLETION TRIGGERED ===")
        print(f"level_index: {level_index}")
        print(f"max_level_reached: {quiz_state.get('max_level_reached', 0)}")
        print(f"final_summary length: {len(quiz_state.get('final_summary', []))}")
        
        from feedback.services import FeedbackService
        
        # Prepare data for feedback service
        teacher_id = request.session.get('quiz_teacher_id')
        syllabus_id = request.session.get('quiz_syllabus_id')
        student_user = request.user
        max_level_reached = quiz_state.get('max_level_reached', 0)
        question_results = quiz_state.get('final_summary', [])
        
        print(f"teacher_id: {teacher_id}, syllabus_id: {syllabus_id}")
        print(f"user: {student_user.username if student_user.is_authenticated else 'Anonymous'}")
        
        # Save feedback to database
        feedback_record = FeedbackService.save_quiz_feedback(
            student_user=student_user,
            teacher_id=teacher_id,
            syllabus_id=syllabus_id,
            quiz_type='descriptive',
            max_level_reached=max_level_reached,
            question_results=question_results
        )
        
        print(f"feedback_record created: {feedback_record}")
        
        # Clean up session
        request.session.pop('desc_quiz_state', None)
        request.session.pop('current_question_data', None)
        
        if feedback_record:
            print(f"Redirecting to feedback page with ID: {feedback_record.id}")
            return redirect('feedback:detailed_feedback', feedback_id=feedback_record.id)
        else:
            # Fallback to old template if feedback saving fails
            print("Feedback saving failed, using fallback template")
            reason = "Congratulations!" if level_index >= len(BLOOM_LEVELS) else "Quiz ended."
            return render(request, 'students/quiz_complete_descriptive.html', {
                'summary': quiz_state['final_summary'], 'reason': reason
            })
    
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, teacher_id=teacher_id)
    level_name = BLOOM_LEVELS[level_index]
    
    descriptive_question = None
    for i in range(3):  # Retry up to 3 times
        print(f"Attempt {i+1} to generate a unique descriptive question for level '{level_name}'...")
        
        instruction = LEVEL_INSTRUCTIONS_DESCRIPTIVE[level_name]
        
        # Add randomness and variety to prevent same questions
        variety_prompts = [
            "Focus on a different concept or module from the syllabus.",
            "Choose a topic that hasn't been covered in previous questions.",
            "Explore a practical application or real-world scenario.",
            "Create a question about advanced concepts in the syllabus.",
            "Focus on fundamental principles and theory.",
            "Generate a question about implementation details."
        ]
        
        random_variety = random.choice(variety_prompts)
        random_seed = random.randint(1000, 9999)
        
        # Get topics already covered to ensure variety
        covered_topics = quiz_state.get('asked_topics', [])
        topic_instruction = f"AVOID these already covered topics: {', '.join(covered_topics)}" if covered_topics else "Cover any relevant topic from the syllabus."
        
        prompt = f"""
        Session: {quiz_state.get('session_id', 'default')} | Seed: {random_seed}
        
        BLOOM'S TAXONOMY LEVEL: {level_name.upper()}
        LEVEL DEFINITION: 
        - Remember: Recalling facts and basic concepts
        - Understand: Explaining ideas or concepts  
        - Apply: Using information in a new situation
        - Analyze: Breaking down information into parts
        - Evaluate: Justifying a stand or decision
        - Create: Producing new or original work
        
        CURRENT LEVEL FOCUS: You must create a {level_name.upper()} level question ONLY.
        
        Here is the entire course syllabus:
        ---
        {syllabus.content}
        ---
        
        Your task: {instruction}
        
        DIVERSITY REQUIREMENT: {random_variety}
        TOPIC VARIETY: {topic_instruction}
        
        CRITICAL RULE: Do NOT repeat any of the following questions:
        ---
        {', '.join(quiz_state['asked_questions'])}
        ---
        
        STRICT LEVEL REQUIREMENTS FOR {level_name.upper()}:
        """ + ("REMEMBER LEVEL: Ask ONLY for basic definitions, facts, or simple recall. NO scenarios, applications, or explanations required." if level_name == "remember" else 
               "UNDERSTAND LEVEL: Ask for explanations or descriptions of how something works. NO complex applications." if level_name == "understand" else
               "APPLY LEVEL: Present a specific scenario and ask how to use a concept to solve it." if level_name == "apply" else
               "ANALYZE LEVEL: Ask to compare, contrast, or break down concepts into parts." if level_name == "analyze" else
               "EVALUATE LEVEL: Ask for judgment or assessment with justification." if level_name == "evaluate" else
               "CREATE LEVEL: Ask to design, propose, or create something new.") + f"""
        
        GOOD EXAMPLES for {level_name.upper()} level:
        """ + (
            "- 'What is a Python function?'\n        - 'Define what a module is in Python'\n        - 'What are the basic data types in Python?'" if level_name == "remember" else
            "- 'Explain how Python functions work'\n        - 'Describe the difference between lists and tuples'" if level_name == "understand" else  
            "- 'You need to store student grades - which data structure would you use and how?'\n        - 'How would you use a function to calculate the average of a list?'" if level_name == "apply" else
            "- 'Compare the advantages of lists vs dictionaries'\n        - 'Analyze when to use functions vs classes'" if level_name == "analyze" else
            "- 'Evaluate which loop type is better for this scenario and justify'\n        - 'Assess the best approach for error handling in this case'" if level_name == "evaluate" else
            "- 'Design a program structure for a calculator'\n        - 'Create a plan for organizing code into modules'"
        ) + f"""
        
        BAD EXAMPLES for {level_name.upper()} level (AVOID):
        """ + (
            "- Questions asking for explanations, scenarios, or applications\n        - Questions with 'explain', 'describe', 'how would you'\n        - Complex multi-part questions" if level_name == "remember" else
            "- Simple definition questions\n        - Questions asking for application or problem-solving\n        - Questions requiring analysis or evaluation" if level_name == "understand" else
            "- Simple definition or explanation questions\n        - Questions without specific scenarios\n        - Questions asking for analysis or evaluation" if level_name == "apply" else
            "- Simple recall or explanation questions\n        - Questions without comparison or breakdown requirements\n        - Questions asking for application only" if level_name == "analyze" else
            "- Questions without judgment or assessment requirements\n        - Simple application or analysis questions\n        - Questions without justification requirements" if level_name == "evaluate" else
            "- Questions asking for analysis, application, or explanation only\n        - Questions without creative or design requirements"
        ) + f"""
        
        IMPORTANT GUIDELINES FOR KEYWORDS:
        1. Choose UNIQUE, specific keywords (no duplicates in the list)
        2. Focus on technical terms, concepts, and key processes
        3. Avoid common words like 'and', 'or', 'the', 'is', 'are', 'can', 'will'
        4. Keywords should be nouns, verbs, or adjectives that are central to the topic
        5. Order keywords logically as they would appear in a good answer
        6. Each keyword should add distinct value to the evaluation
        
        IMPORTANT GUIDELINES FOR QUESTIONS:
        1. Choose a DIFFERENT topic/concept from previous questions
        2. Ensure the question is unique and not similar to previous ones
        3. Make the question clear and specific
        4. MUST match the {level_name.upper()} level requirements exactly
        5. Focus on one main concept or process
        
        Format your response STRICTLY as follows:
        Topic: [Name of the Module/Topic you chose - make it DIFFERENT from previous topics]
        Question: [The {level_name} level question text - must match level requirements]
        Keywords: [keyword1, keyword2, keyword3, keyword4]
        
        VERIFY: Before finalizing, check that your question truly matches {level_name.upper()} level requirements!
        """
        
        chat_history = quiz_state['chat_history']
        
        # Clear chat history periodically to prevent AI from getting stuck in patterns
        if len(chat_history) > 10:  # Keep only recent context
            system_msg = chat_history[0:2]  # Keep system instruction
            recent_context = chat_history[-4:]  # Keep last 2 exchanges
            chat_history = system_msg + recent_context
            quiz_state['chat_history'] = chat_history
        
        chat_history.append({'role': 'user', 'parts': [prompt]})
        
        try:
            response = MODEL.generate_content(chat_history)
            chat_history.append({'role': 'model', 'parts': [response.text]})
            parsed_question = parse_descriptive_response(response.text)
            if parsed_question and parsed_question.get('question') not in quiz_state['asked_questions']:
                descriptive_question = parsed_question
                # Track the topic to ensure variety in future questions
                if 'asked_topics' not in quiz_state:
                    quiz_state['asked_topics'] = []
                quiz_state['asked_topics'].append(parsed_question.get('topic', 'General'))
                break
        except Exception as e:
            print(f"API Error: {e}")
            continue

    quiz_state['chat_history'] = chat_history

    if not descriptive_question:
        print("=== FAILED TO GENERATE QUESTION ===")
        print(f"Attempts made, level: {level_name}")
        print(f"Already asked: {quiz_state['asked_questions']}")
        messages.error(request, "Failed to generate a unique question. Please try again.")
        request.session.pop('desc_quiz_state', None)
        return redirect('students:dashboard')

    print(f"=== QUESTION GENERATED SUCCESSFULLY ===")
    print(f"Question: {descriptive_question.get('question', 'N/A')[:100]}...")
    print(f"Keywords: {descriptive_question.get('keywords', [])}")
    print(f"Topic: {descriptive_question.get('topic', 'N/A')}")

    request.session['current_question_data'] = descriptive_question
    request.session['desc_quiz_state'] = quiz_state
    
    return render(request, 'students/descriptive_quiz.html', {
        'question_data': descriptive_question,
        'level_name': level_name.capitalize(),
        'current_q_num': quiz_state['questions_answered_in_level'] + 1,
        'total_q_in_level': num_per_taxonomy,
        'topic': descriptive_question.get('topic', 'General')
    })
