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
MODEL = genai.GenerativeModel('gemini-1.5-flash')
BLOOM_LEVELS = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']

# --- NEW: Level-Specific Instructions for Descriptive Questions ---
LEVEL_INSTRUCTIONS_DESCRIPTIVE = {
    "remember": "Generate a direct, factual question that requires recalling a definition or specific term from the syllabus. Provide 4-5 essential, unique keywords that must appear in a correct answer (avoid duplicates).",
    "understand": "Generate a question that requires the user to explain a concept in their own words or describe how something works. Provide 5-6 unique, meaningful keywords that represent core concepts in a logical sequence.",
    "apply": "Generate a question that presents a simple problem scenario and asks how a specific concept would be used to solve it. Provide 5-7 unique keywords that represent the key steps or elements in the solution process.",
    "analyze": "Generate a question that requires breaking down a concept into parts or comparing concepts. Provide 6-7 unique keywords that represent the analytical components or comparison points.",
    "evaluate": "Generate a question asking for judgment or assessment of a concept based on criteria. Provide 6-8 unique keywords that represent evaluation criteria and reasoning elements.",
    "create": "Generate a question asking to propose, design, or outline something new. Provide 7-8 unique keywords representing the creative process, components, or implementation steps."
}

# --- Helper Functions ---
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
    Enhanced evaluation that checks for token sequence matching with proper order consideration.
    """
    if not student_answer or not ai_keywords:
        return 0.0

    # Tokenize student answer
    student_tokens = tokenize_text(student_answer)
    
    if not student_tokens or not ai_keywords:
        return 0.0
    
    print(f"AI Keywords: {ai_keywords}")
    print(f"Student Tokens (first 15): {student_tokens[:15]}")
    
    # Method 1: Sequential token matching (strict order)
    matches = 0
    student_idx = 0
    matched_keywords = []
    
    for keyword in ai_keywords:
        found = False
        # Look for the keyword starting from current position
        for i in range(student_idx, len(student_tokens)):
            token = student_tokens[i]
            # Check for exact match or partial match (both ways)
            if (keyword == token or 
                (len(keyword) > 3 and keyword in token) or 
                (len(token) > 3 and token in keyword)):
                matches += 1
                matched_keywords.append(f"{keyword}→{token}")
                student_idx = i + 1
                found = True
                break
        
        if not found:
            # If not found in sequence, mark the position anyway to continue
            pass
    
    sequence_score = (matches / len(ai_keywords)) * 100
    
    # Method 2: Overall keyword presence (any order)
    presence_matches = 0
    presence_details = []
    
    for keyword in ai_keywords:
        found_anywhere = False
        for token in student_tokens:
            if (keyword == token or 
                (len(keyword) > 3 and keyword in token) or 
                (len(token) > 3 and token in keyword)):
                presence_matches += 1
                presence_details.append(f"{keyword}↔{token}")
                found_anywhere = True
                break
        
        if not found_anywhere:
            presence_details.append(f"{keyword}✗missing")
    
    presence_score = (presence_matches / len(ai_keywords)) * 100
    
    # Method 3: Semantic overlap scoring
    # Count how many student tokens are semantically related to keywords
    semantic_matches = 0
    for token in student_tokens:
        for keyword in ai_keywords:
            if (keyword == token or 
                (len(keyword) > 3 and keyword in token) or 
                (len(token) > 3 and token in keyword)):
                semantic_matches += 1
                break
    
    # Avoid division by zero and calculate semantic density
    semantic_score = min(100, (semantic_matches / max(len(student_tokens), 1)) * 100)
    
    # Combine scores with weighted average
    # 50% sequence order, 35% presence, 15% semantic density
    final_score = (sequence_score * 0.5) + (presence_score * 0.35) + (semantic_score * 0.15)
    
    print(f"Sequential matches: {matches}/{len(ai_keywords)} = {sequence_score:.1f}%")
    print(f"  → Matched: {matched_keywords}")
    print(f"Presence matches: {presence_matches}/{len(ai_keywords)} = {presence_score:.1f}%")
    print(f"  → Details: {presence_details}")
    print(f"Semantic density: {semantic_matches}/{len(student_tokens)} tokens = {semantic_score:.1f}%")
    print(f"Final weighted score: {final_score:.2f}%")
    
    return final_score

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
        
        match_score = evaluate_answer_with_token_sequence(student_answer, current_question.get('keywords', []))
        is_correct = match_score >= 70.0

        if is_correct:
            quiz_state['correct_in_level'] += 1
        
        quiz_state['questions_answered_in_level'] += 1
        quiz_state['asked_questions'].append(current_question.get('question'))  # Add to simple list
        quiz_state['final_summary'].append({
            'level': BLOOM_LEVELS[quiz_state['level_index']],
            'question': current_question.get('question'),
            'student_answer': student_answer,
            'match_score': f"{match_score:.1f}%",
            'is_correct': is_correct,
            'topic': current_question.get('topic', 'General')
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
        4. Focus on one main concept or process
        
        Format your response STRICTLY as follows:
        Topic: [Name of the Module/Topic you chose - make it DIFFERENT from previous topics]
        Question: [The descriptive question text - ensure it's UNIQUE and DIFFERENT]
        Keywords: [keyword1, keyword2, keyword3, keyword4, keyword5]
        
        EXAMPLE of GOOD keywords for a Python function question:
        Keywords: function, parameters, return, statement, scope
        
        EXAMPLE of BAD keywords (avoid these patterns):
        Keywords: function, and, function, the, parameters, is, return  # duplicates, stopwords
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
        messages.error(request, "Failed to generate a unique question. Please try again.")
        request.session.pop('desc_quiz_state', None)
        return redirect('students:dashboard')

    request.session['current_question_data'] = descriptive_question
    request.session['desc_quiz_state'] = quiz_state
    
    return render(request, 'students/descriptive_quiz.html', {
        'question_data': descriptive_question,
        'level_name': level_name.capitalize(),
        'current_q_num': quiz_state['questions_answered_in_level'] + 1,
        'total_q_in_level': num_per_taxonomy,
        'topic': descriptive_question.get('topic', 'General')
    })
