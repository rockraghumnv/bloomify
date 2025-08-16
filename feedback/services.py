from .models import QuizFeedback, QuizQuestionResult
from django.contrib.auth.models import User
from teachers.models import Syllabus

class FeedbackService:
    """
    Service class to handle quiz feedback generation and storage
    """
    
    @staticmethod
    def get_feedback_message(max_level_reached):
        """
        Generate feedback message based on the maximum level reached
        """
        feedback_messages = {
            0: {
                'level': 'basic',
                'message': 'You need to work on the fundamentals. Focus on understanding basic concepts and definitions. Review the syllabus thoroughly and practice more foundational questions.'
            },
            1: {
                'level': 'basic', 
                'message': 'Basic knowledge is there but still work on advanced concepts. You understand the fundamentals but need to practice applying them in different scenarios.'
            },
            2: {
                'level': 'intermediate',
                'message': 'Intermediate knowledge achieved! Try building projects and practical applications. You have a good grasp of concepts and can apply them effectively.'
            },
            3: {
                'level': 'intermediate',
                'message': 'Good intermediate knowledge! You can analyze concepts well. Consider working on more complex problems and real-world applications to advance further.'
            },
            4: {
                'level': 'advanced',
                'message': 'Really good knowledge! You have excellent analytical and evaluation skills. To master the highest level, go deeper into the concepts and explore advanced applications.'
            },
            5: {
                'level': 'excellent',
                'message': 'Excellent level knowledge! Keep it up! You have mastered all Bloom\'s taxonomy levels and can create and innovate with the concepts. Well done!'
            }
        }
        
        return feedback_messages.get(max_level_reached, feedback_messages[0])
    
    @staticmethod
    def calculate_accuracy(question_results):
        """
        Calculate overall accuracy from question results
        """
        if not question_results:
            return 0.0
        
        total_questions = len(question_results)
        correct_answers = sum(1 for result in question_results if result['is_correct'])
        
        return (correct_answers / total_questions) * 100
    
    @staticmethod
    def save_quiz_feedback(student_user, teacher_id, syllabus_id, quiz_type, max_level_reached, question_results):
        """
        Save comprehensive quiz feedback to database
        """
        try:
            # Get teacher and syllabus
            teacher = User.objects.get(id=teacher_id)
            syllabus = Syllabus.objects.get(id=syllabus_id, teacher=teacher)
            
            # Get feedback details
            feedback_info = FeedbackService.get_feedback_message(max_level_reached)
            accuracy = FeedbackService.calculate_accuracy(question_results)
            
            # Create main feedback record
            quiz_feedback = QuizFeedback.objects.create(
                student=student_user,
                teacher=teacher,
                syllabus=syllabus,
                quiz_type=quiz_type,
                max_level_reached=max_level_reached,
                feedback_level=feedback_info['level'],
                feedback_message=feedback_info['message'],
                total_questions_attempted=len(question_results),
                total_correct_answers=sum(1 for result in question_results if result['is_correct']),
                accuracy_percentage=accuracy
            )
            
            # Create individual question results
            for result in question_results:
                QuizQuestionResult.objects.create(
                    feedback=quiz_feedback,
                    bloom_level=result.get('level', ''),
                    question_text=result.get('question', ''),
                    student_answer=result.get('student_answer', ''),
                    correct_option=result.get('correct_option', ''),
                    selected_option=result.get('selected_option', ''),
                    expected_keywords=result.get('expected_keywords', []),
                    matched_keywords=result.get('matched_keywords', {}),
                    is_correct=result.get('is_correct', False),
                    score_percentage=result.get('score_percentage', 0.0),
                    topic=result.get('topic', '')
                )
            
            return quiz_feedback
            
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return None
    
    @staticmethod
    def get_student_feedbacks(student_user):
        """
        Get all feedback records for a student
        """
        return QuizFeedback.objects.filter(student=student_user).order_by('-created_at')
    
    @staticmethod
    def get_feedback_details(feedback_id):
        """
        Get detailed feedback with all question results
        """
        try:
            feedback = QuizFeedback.objects.get(id=feedback_id)
            question_results = feedback.question_results.all()
            
            return {
                'feedback': feedback,
                'question_results': question_results
            }
        except QuizFeedback.DoesNotExist:
            return None
