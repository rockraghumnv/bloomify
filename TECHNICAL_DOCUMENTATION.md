# Bloomify Quiz System - Technical Documentation

## Overview
Bloomify is a Django-based adaptive learning platform that uses Bloom's Taxonomy to assess students' cognitive abilities through dynamic quizzes. It leverages Google's Gemini AI to generate personalized questions at different complexity levels.

---

## 1. SYSTEM FLOW

### 1.1 Overall Application Flow

```
Student Login → Dashboard → Select Quiz Type → Quiz Execution → Results/Feedback
                    ↑                              ↓
                    └──────── Review History ──────┘
```

### 1.2 MCQ Quiz Flow (Dynamic Quiz)

#### Phase 1: Initialization
1. **Student Selection**: Student selects syllabus and questions per taxonomy level
2. **Session Setup**: System initializes quiz state in session storage
   - Sets level_index = 0 (Remember level)
   - Creates unique session_id for AI diversity
   - Initializes empty chat history with Gemini AI
   - Sets up tracking for asked questions and topics

#### Phase 2: Question Generation Loop
1. **Level Determination**: System checks current Bloom's level
2. **AI Prompt Construction**: 
   - Includes entire syllabus content
   - Adds level-specific instructions
   - Implements anti-repetition mechanisms
   - Injects randomness seeds and variety prompts
3. **Gemini API Call**: Sends prompt to generate unique MCQ
4. **Response Parsing**: Extracts question, options, correct answer, and topic
5. **Uniqueness Check**: Verifies question hasn't been asked before
6. **Retry Mechanism**: Up to 3 attempts if parsing fails or question repeats

#### Phase 3: Answer Evaluation
1. **Student Submission**: Captures selected answer
2. **Correctness Check**: Compares with correct answer
3. **Score Tracking**: Updates correct_in_level counter
4. **Result Storage**: Saves detailed result including:
   - Level, question, student answer, correct answer
   - Score percentage, topic, all options

#### Phase 4: Level Progression Logic
```
After completing N questions at current level:
├─ IF score >= pass_marks:
│  ├─ Level UP (move to next Bloom's level)
│  └─ Reset consecutive_failures counter
└─ ELSE (failed level):
   ├─ IF level == 0 (Remember):
   │  └─ EXIT quiz immediately
   └─ ELSE:
      ├─ Increment consecutive_failures
      ├─ IF consecutive_failures >= 2:
      │  └─ EXIT quiz
      └─ ELSE:
         └─ Level DOWN (downgrade one level)
```

**Pass Marks Table**:
- 3 questions per level → Need 2 correct (67%)
- 6 questions per level → Need 4 correct (67%)
- 8 questions per level → Need 6 correct (75%)

#### Phase 5: Quiz Completion
1. **Feedback Generation**: Calls FeedbackService to save results
2. **Data Package**: Sends all question results and max level reached
3. **Database Storage**: Creates QuizFeedback record
4. **Redirect**: Takes student to detailed feedback page

### 1.3 Descriptive Quiz Flow

#### Initialization
Similar to MCQ but uses separate session key: `desc_quiz_state`

#### Question Generation
1. **Enhanced Level Instructions**: Uses detailed Bloom's taxonomy descriptions
2. **Keyword-Based Evaluation**: AI generates evaluation keywords along with question
3. **Topic Diversity**: Tracks covered topics to ensure variety

#### Answer Evaluation Algorithm
1. **Tokenization**: Breaks student answer into meaningful tokens
   - Removes stopwords (200+ common words)
   - Normalizes hyphens, underscores
   - Filters short words (< 2 chars)

2. **Keyword Matching**:
   - Exact phrase matching in normalized text
   - Synonym expansion (50+ synonym mappings)
   - Multi-word keyword detection
   - Partial token matching

3. **Scoring System**:
   ```
   base_score = (matched_keywords / total_keywords) × 100
   
   IF coverage >= 80%: bonus = 10%
   ELSE IF coverage >= 60%: bonus = 5%
   
   final_score = min(base_score + bonus, 100)
   ```

4. **Feedback Storage**: Saves matched/unmatched keywords for detailed feedback

---

## 2. TECHNIQUES USED

### 2.1 AI Integration Techniques

#### **Conversational Memory**
- Maintains chat history with Gemini AI
- Preserves context across question generations
- Prunes history when > 10 entries to prevent pattern lock

#### **Prompt Engineering**
- **Structured Prompts**: Clear format requirements (Question:, A), B), etc.)
- **Anti-Repetition**: Explicitly lists previously asked questions
- **Randomization Instructions**: Explicitly tells AI to randomize correct answer position
- **Length Balancing**: Instructs AI to keep all options similar length
- **Diversity Injection**: Adds random variety prompts and unique seeds

#### **Error Handling & Retry Logic**
- Try-catch blocks around API calls
- Up to 3 retry attempts per question
- Fallback to graceful error messages

### 2.2 Session Management Techniques

#### **State Persistence**
```python
quiz_state = {
    'level_index': int,           # Current Bloom's level
    'questions_answered_in_level': int,
    'correct_in_level': int,
    'max_level_reached': int,
    'consecutive_failures': int,
    'session_id': str,            # Unique identifier for randomness
    'asked_questions': list,      # Prevent repeats
    'asked_topics': list,         # Ensure topic diversity
    'final_summary': list,        # Detailed results
    'chat_history': list          # AI conversation context
}
```

#### **Session Isolation**
- Separate keys for MCQ (`quiz_state`) and descriptive (`desc_quiz_state`)
- Explicit session cleanup when starting new quiz
- Safety mechanism: auto-exit if questions exceed maximum

### 2.3 Parsing Techniques

#### **Robust Line-by-Line Parsing**
```python
# Handles multi-line code snippets in options
# Uses state machine approach:
# - Detects option start (A), B), C), D))
# - Buffers lines until next option
# - Preserves indentation for code options
```

#### **Regex-Based Extraction**
- Pattern matching for option labels: `^[A-D]\)`
- Field detection: `Question:`, `Topic:`, `Correct:`
- Normalization of AI response variations

### 2.4 Text Analysis Techniques

#### **Advanced Tokenization**
1. Lowercase normalization
2. Punctuation removal (preserving hyphens)
3. Whitespace normalization
4. Stopword filtering (200+ words)
5. Duplicate removal with order preservation

#### **Synonym Expansion**
- Pre-defined synonym mappings for technical terms
- Handles variations: function/func/method/procedure
- Supports compound word matching: while-loop, while loop, while_loop

#### **Flexible Keyword Matching**
```python
# Multi-strategy matching:
1. Exact phrase match in normalized text
2. Token sequence matching (multi-word keywords)
3. Single token matching with synonyms
4. Partial matching for flexibility
```

### 2.5 Security & Validation Techniques

- **Login Required Decorators**: `@method_decorator(login_required)`
- **Object Verification**: `get_object_or_404()` prevents invalid access
- **Session Validation**: Checks for required session keys
- **Input Sanitization**: Validates form inputs before processing

---

## 3. ALGORITHMS

### 3.1 Question Generation Algorithm

```
ALGORITHM: GenerateUniqueQuestion(level, syllabus, asked_questions)

INPUT: 
  - level: Current Bloom's taxonomy level (0-5)
  - syllabus: Course content
  - asked_questions: List of previously asked questions

OUTPUT:
  - Parsed MCQ or None

STEPS:
1. max_attempts ← 3
2. FOR i ← 1 TO max_attempts:
   
   3. Generate random_seed and select random variety_prompt
   
   4. Build AI prompt:
      - Include full syllabus content
      - Add level-specific instructions from LEVEL_INSTRUCTIONS[level]
      - Add diversity requirements (variety_prompt)
      - Include topic avoidance list (asked_topics)
      - List all asked_questions to prevent repetition
      - Add randomization instructions (position, length, distractors)
   
   5. Append prompt to chat_history
   
   6. TRY:
      7. response ← MODEL.generate_content(chat_history)
      8. Append response to chat_history
      
      9. parsed_mcq ← parse_question_from_response(response.text)
      
      10. IF parsed_mcq is valid AND 
            parsed_mcq.question NOT IN asked_questions:
         11. Add parsed_mcq.topic to asked_topics
         12. RETURN parsed_mcq
   
   CATCH Exception e:
      13. Log error and continue to next attempt

14. RETURN None  // Failed after max_attempts
```

### 3.2 MCQ Parsing Algorithm

```
ALGORITHM: ParseQuestionFromResponse(response_text)

INPUT: response_text: String from AI

OUTPUT: Dictionary with {question, options, correct_answer, topic} or None

STEPS:
1. lines ← Split response_text by '\n'
2. question ← "", topic ← "", correct_letter ← ""
3. options ← empty dictionary
4. current_option_key ← None
5. buffer ← empty list

6. FOR EACH line IN lines:
   7. stripped_line ← trim(line)
   
   8. IF stripped_line is empty: CONTINUE
   
   9. IF starts_with("Question:", case_insensitive):
      10. question ← extract_text_after("Question:")
   
   11. ELSE IF starts_with("Topic:", case_insensitive):
      12. topic ← extract_text_after("Topic:")
   
   13. ELSE IF starts_with("Correct:", case_insensitive):
      14. IF current_option_key exists:
         15. options[current_option_key] ← join(buffer)
      16. correct_letter ← extract_text_after("Correct:").upper()
      17. current_option_key ← None
   
   18. ELSE IF matches_pattern("^[A-D]\)", case_insensitive):
      19. IF current_option_key exists:  // Save previous option
         20. options[current_option_key] ← join(buffer)
      
      21. current_option_key ← first_character.upper()
      22. buffer ← [text_after_closing_paren]
   
   23. ELSE IF current_option_key exists:
      24. buffer.append(line)  // Preserve indentation

25. IF question exists AND 
      options.length == 4 AND 
      correct_letter IN options:
   26. ordered_options ← [options['A'], options['B'], options['C'], options['D']]
   27. RETURN {
         question: question,
         options: ordered_options,
         correct_answer: options[correct_letter],
         topic: topic OR "General"
      }

28. Log parsing failure with response_text
29. RETURN None
```

### 3.3 Adaptive Level Progression Algorithm

```
ALGORITHM: UpdateLevelProgression(quiz_state, is_correct, num_per_taxonomy)

INPUT:
  - quiz_state: Current quiz state dictionary
  - is_correct: Boolean indicating if answer was correct
  - num_per_taxonomy: Questions per level

OUTPUT: Updated quiz_state

STEPS:
1. IF is_correct:
   2. quiz_state.correct_in_level ← quiz_state.correct_in_level + 1

3. quiz_state.questions_answered_in_level ← quiz_state.questions_answered_in_level + 1

4. IF quiz_state.questions_answered_in_level >= num_per_taxonomy:
   
   5. pass_marks_map ← {3: 2, 6: 4, 8: 6}
   6. required_to_pass ← pass_marks_map[num_per_taxonomy] OR 2
   
   7. IF quiz_state.correct_in_level >= required_to_pass:
      // PASSED THIS LEVEL
      8. quiz_state.level_index ← quiz_state.level_index + 1
      9. quiz_state.consecutive_failures ← 0
      
      10. IF quiz_state.level_index > quiz_state.max_level_reached:
          11. quiz_state.max_level_reached ← quiz_state.level_index
   
   ELSE:
      // FAILED THIS LEVEL
      12. quiz_state.consecutive_failures ← quiz_state.consecutive_failures + 1
      
      13. IF quiz_state.level_index == 0:  // Failed Remember level
          14. quiz_state.level_index ← -1  // Exit quiz
      
      15. ELSE IF quiz_state.consecutive_failures >= 2:
          16. quiz_state.level_index ← -1  // Exit after 2 consecutive failures
      
      17. ELSE:
          18. quiz_state.level_index ← quiz_state.level_index - 1  // Downgrade
   
   // Reset level counters
   19. quiz_state.correct_in_level ← 0
   20. quiz_state.questions_answered_in_level ← 0

21. RETURN quiz_state
```

### 3.4 Descriptive Answer Evaluation Algorithm

```
ALGORITHM: EvaluateDescriptiveAnswer(student_answer, ai_keywords)

INPUT:
  - student_answer: String (student's written response)
  - ai_keywords: List of evaluation keywords from AI

OUTPUT: {score, matched_keywords, unmatched_keywords, details}

STEPS:
1. student_tokens ← tokenize_text(student_answer)
2. student_text_normalized ← normalize_keyword(student_answer)

3. matches ← 0
4. matched_keywords ← empty list
5. unmatched_keywords ← empty list

6. FOR EACH keyword IN ai_keywords:
   
   7. normalized_keyword ← normalize_keyword(keyword)
   8. is_multiword ← keyword contains spaces
   9. found ← False
   
   10. // Strategy 1: Exact phrase matching
   11. IF normalized_keyword IN student_text_normalized:
       12. found ← True
   
   13. ELSE IF is_multiword:
       // Strategy 2: Token sequence matching
       14. keyword_tokens ← split(normalized_keyword)
       15. IF all_consecutive_in(keyword_tokens, student_tokens):
           16. found ← True
   
   17. ELSE:
       // Strategy 3: Synonym expansion matching
       18. synonyms ← get_keyword_synonyms(keyword)
       19. FOR EACH syn IN synonyms:
           20. IF syn IN student_text_normalized OR 
                 syn IN student_tokens:
               21. found ← True
               22. BREAK
   
   23. IF found:
       24. matches ← matches + 1
       25. matched_keywords.append(keyword)
   26. ELSE:
       27. unmatched_keywords.append(keyword)

28. total_possible ← length(ai_keywords)
29. base_score ← (matches / total_possible) × 100
30. coverage_ratio ← matches / total_possible

31. // Bonus scoring
32. bonus ← 0
33. IF coverage_ratio >= 0.8:
    34. bonus ← 10
35. ELSE IF coverage_ratio >= 0.6:
    36. bonus ← 5

37. final_score ← min(base_score + bonus, 100.0)

38. RETURN {
    final_score: final_score,
    matched_count: matches,
    total_keywords: total_possible,
    coverage_ratio: coverage_ratio,
    matched_keywords: matched_keywords,
    unmatched_keywords: unmatched_keywords
}
```

### 3.5 Text Tokenization Algorithm

```
ALGORITHM: TokenizeText(text)

INPUT: text: String to tokenize

OUTPUT: List of meaningful tokens

STEPS:
1. text ← lowercase(text)
2. text ← replace_pattern(text, '[^\w\s-]', ' ')  // Remove punctuation except hyphens
3. text ← replace_pattern(text, '\s+', ' ')       // Normalize whitespace
4. words ← split(text, ' ')

5. stopwords ← {200+ common English words}  // Pre-defined set

6. tokens ← empty list
7. seen ← empty set

8. FOR EACH word IN words:
   9. IF length(word) >= 2 AND 
         word NOT IN stopwords AND 
         word NOT IN seen:
      10. tokens.append(word)
      11. seen.add(word)

12. RETURN tokens
```

---

## 4. DATA STRUCTURES

### 4.1 Quiz State Structure
```python
{
    'level_index': int,                    # 0-5 for Bloom's levels, -1 for exit
    'questions_answered_in_level': int,    # Counter for current level
    'correct_in_level': int,               # Correct answers in current level
    'max_level_reached': int,              # Highest level achieved
    'consecutive_failures': int,           # Failure tracking for exit logic
    'session_id': str,                     # Unique session identifier
    'asked_questions': [str],              # List of question texts
    'asked_topics': [str],                 # List of covered topics
    'final_summary': [{                    # Detailed results per question
        'level': str,
        'question': str,
        'student_answer': str,
        'correct_option': str,
        'selected_option': str,
        'score_percentage': float,
        'is_correct': bool,
        'topic': str,
        'options': {A, B, C, D}
    }],
    'chat_history': [{                     # Gemini AI conversation
        'role': str,                       # 'user' or 'model'
        'parts': [str]
    }]
}
```

### 4.2 Parsed Question Structure (MCQ)
```python
{
    'question': str,                       # Question text
    'options': [str, str, str, str],      # Ordered A, B, C, D
    'correct_answer': str,                # Text of correct option
    'topic': str                          # Topic/module name
}
```

### 4.3 Parsed Question Structure (Descriptive)
```python
{
    'question': str,                       # Question text
    'keywords': [str],                     # Evaluation keywords
    'topic': str                          # Topic/module name
}
```

---

## 5. KEY DESIGN PATTERNS

### 5.1 State Machine Pattern
The quiz progression follows a state machine with states:
- **Remember → Understand → Apply → Analyze → Evaluate → Create**
- Transitions based on performance
- Can move forward (pass) or backward (fail)
- Terminal states: Exit (-1) or Complete (6)

### 5.2 Strategy Pattern
Different question types use different strategies:
- **MCQ Strategy**: Exact match comparison
- **Descriptive Strategy**: Token-based fuzzy matching
- Encapsulated in separate files: `dynamic_quiz_logic.py` and `descriptive_quiz_logic.py`

### 5.3 Template Method Pattern
Both quiz types follow the same high-level flow:
1. Initialize state
2. Generate question
3. Present to student
4. Evaluate answer
5. Update progression
6. Repeat or exit

### 5.4 Retry Pattern
Question generation uses exponential retry:
- Attempt 1: Standard generation
- Attempt 2: Retry with same logic
- Attempt 3: Final attempt
- Fail gracefully if all attempts exhausted

---


---

## 7. ERROR HANDLING STRATEGIES

### 7.1 API Failure Handling
```
Try API call
├─ Success → Parse and validate
├─ Parse failure → Retry (up to 3 attempts)
└─ API error → Log and retry
```

##
---

#


## Conclusion

Bloomify implements a sophisticated adaptive learning system that combines:
- AI-powered question generation
- Bloom's Taxonomy-based assessment
- Intelligent level progression
- Robust text analysis
- Comprehensive feedback mechanisms

The modular architecture allows for easy extension and maintenance while providing a rich, personalized learning experience for students.
