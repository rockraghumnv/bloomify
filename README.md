# Bloomify 🌸
**An Intelligent Quiz Platform Based on Bloom's Taxonomy**

Bloomify is a Django-based educational platform that creates adaptive quizzes based on Bloom's Taxonomy cognitive levels. The platform uses AI to generate questions and provides detailed performance feedback to help students track their learning progress.

## 🚀 Features

### 🎯 Adaptive Quiz System
- **Bloom's Taxonomy Integration**: Questions are categorized into 6 cognitive levels (Remember, Understand, Apply, Analyze, Evaluate, Create)
- **Progressive Difficulty**: Students advance through taxonomy levels based on performance
- **Duplicate Prevention**: Intelligent system prevents repeated questions within quiz sessions

### 📝 Two Quiz Types

#### 1. **Multiple Choice Questions (MCQ)**
- AI-generated questions with 4 options
- Immediate feedback on answers
- Configurable question count (3, 6, or 8 per taxonomy level)
- Proper code formatting for programming questions

#### 2. **Descriptive Questions**
- Open-ended questions requiring detailed answers
- Advanced AI evaluation using keyword matching
- Enhanced token analysis with synonym recognition
- Fixed at 3 questions per taxonomy level for optimal assessment

### 🧠 Intelligent Evaluation System
- **Enhanced Token Matching**: Recognizes synonyms, plurals, and technical variations
- **Flexible Phrase Recognition**: Handles different terminology and phrasing
- **Fuzzy Matching**: Accounts for minor spelling variations
- **Contextual Scoring**: Provides bonus points for comprehensive answers

### 📊 Comprehensive Feedback System
- **Detailed Performance Analytics**: Level-wise breakdown of performance
- **Learning Path Recommendations**: Personalized suggestions based on quiz results
- **Historical Progress Tracking**: View all past quiz attempts and improvements
- **Question-Level Analysis**: Individual question feedback with keyword matching details

### 👥 Multi-User Support
- **Teacher Dashboard**: Create and manage syllabi, view student progress
- **Student Dashboard**: Take quizzes, view feedback history, track learning progress
- **Session Management**: Secure user authentication and session handling

## 🛠 Technology Stack

- **Backend**: Django 5.1.7 (Python)
- **Database**: SQLite (default) / PostgreSQL (production)
- **AI Integration**: Google Gemini AI for question generation
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Authentication**: Django's built-in authentication system

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- Google Gemini API key (for AI question generation)

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rockraghumnv/bloomify.git
cd bloomify
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv bloomify_env
bloomify_env\Scripts\activate

# macOS/Linux
python3 -m venv bloomify_env
source bloomify_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 🏗 Project Structure

```
bloomify/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3               # SQLite database
├── README.md                # Project documentation
│
├── bloomify/                # Main project directory
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   │
│   ├── static/              # Static files (CSS, JS, images)
│   │   └── css/
│   │
│   └── templates/           # Global templates
│       ├── base.html        # Base template
│       ├── index.html       # Homepage
│       │
│       ├── registration/    # Authentication templates
│       ├── students/        # Student-specific templates
│       ├── teachers/        # Teacher-specific templates
│       └── feedback/        # Feedback templates
│
├── accounts/                # User management app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── students/                # Student functionality app
│   ├── models.py            # Student-related models
│   ├── urls.py              # Student URL patterns
│   ├── admin.py             # Admin configuration
│   │
│   ├── views/               # Modular view structure
│   │   ├── dashboard.py     # Dashboard logic
│   │   ├── quiz.py          # Quiz management
│   │   ├── dynamic_quiz_logic.py    # MCQ quiz logic
│   │   ├── descriptive_quiz_logic.py # Descriptive quiz logic
│   │   ├── results.py       # Results handling
│   │   └── my_results.py    # Personal results
│   │
│   └── templatetags/        # Custom template tags
│       └── custom_tags.py
│
├── teachers/                # Teacher functionality app
│   ├── models.py            # Syllabus and course models
│   ├── views.py             # Teacher dashboard and management
│   ├── urls.py              # Teacher URL patterns
│   └── admin.py             # Admin configuration
│
└── feedback/                # Feedback system app
    ├── models.py            # Feedback and results models
    ├── views.py             # Feedback display logic
    ├── urls.py              # Feedback URL patterns
    ├── services.py          # Feedback business logic
    └── admin.py             # Admin configuration
```

## 📊 Database Models

### Core Models

#### **Teachers App**
- `Syllabus`: Course content and structure
- `Teacher`: Extended user profile for teachers

#### **Students App**
- `StudentResponse`: MCQ quiz responses
- `StudentFeedback`: Performance summaries
- `DescriptiveQuizSession`: Descriptive quiz sessions

#### **Feedback App**
- `QuizFeedback`: Comprehensive quiz feedback records
- `QuizQuestionResult`: Individual question results and analysis

## 🎮 Usage Guide

### For Teachers

#### 1. **Account Setup**
- Register as a teacher at `/accounts/register/`
- Access teacher dashboard at `/teachers/`

#### 2. **Syllabus Management**
- Create detailed course syllabi
- Structure content by topics and modules
- Update and maintain course materials

#### 3. **Student Monitoring**
- View student quiz attempts
- Analyze performance trends
- Access detailed feedback reports

### For Students

#### 1. **Taking Quizzes**
- **MCQ Quiz**: Select syllabus and question count (3, 6, or 8 per level)
- **Descriptive Quiz**: Select syllabus (fixed 3 questions per level)
- Progress through Bloom's taxonomy levels based on performance

#### 2. **Performance Tracking**
- View detailed feedback after each quiz
- Access comprehensive feedback history at `/feedback/history/`
- Track learning progress over time
- Get personalized learning recommendations

#### 3. **Understanding Results**
- **Level Analysis**: Performance breakdown by Bloom's taxonomy level
- **Question Analysis**: Individual question feedback with keyword matching
- **Learning Path**: Recommendations for improvement
- **Progress Tracking**: Historical performance trends

## 🤖 AI Integration

### Question Generation
- **Gemini AI**: Generates contextual questions based on syllabus content
- **Taxonomy Compliance**: Ensures questions match specified Bloom's levels
- **Diversity**: Prevents repetitive content through intelligent prompting
- **Quality Control**: Multi-attempt generation for optimal question quality

### Answer Evaluation (Descriptive)
- **Keyword Extraction**: AI identifies key concepts in expected answers
- **Synonym Recognition**: Matches student responses with technical variations
- **Contextual Scoring**: Evaluates comprehension beyond exact word matching
- **Detailed Feedback**: Provides insights into answer quality and completeness

## 🔧 Configuration

### Environment Variables
```env
# Debug mode (set to False in production)
DEBUG=True

# Secret key for Django (generate a secure one for production)
SECRET_KEY=your-secret-key-here

# Gemini AI API key
GEMINI_API_KEY=your-gemini-api-key-here

# Database configuration (optional, defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/bloomify
```

### Quiz Configuration
- **MCQ Questions per Level**: 3, 6, or 8 (configurable by student)
- **Descriptive Questions per Level**: 3 (fixed)
- **Pass Threshold**: 70% (configurable in settings)
- **Maximum Retries**: 3 attempts per question generation

## 🚀 Deployment

### Production Setup

#### 1. **Environment Configuration**
```bash
export DEBUG=False
export SECRET_KEY=your-production-secret-key
export GEMINI_API_KEY=your-api-key
export DATABASE_URL=your-production-database-url
```

#### 2. **Database Migration**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

#### 3. **Web Server Setup**
- **Gunicorn**: `gunicorn bloomify.wsgi:application`
- **Nginx**: Configure as reverse proxy
- **SSL**: Enable HTTPS for security

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test students
python manage.py test feedback

# Check system integrity
python manage.py check
```

### Manual Testing Checklist
- [ ] User registration and login
- [ ] MCQ quiz generation and evaluation
- [ ] Descriptive quiz generation and evaluation
- [ ] Feedback system functionality
- [ ] Progress tracking accuracy
- [ ] Admin panel accessibility

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes** and commit them: `git commit -m 'Add new feature'`
4. **Push to the branch**: `git push origin feature/new-feature`
5. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 coding standards
- Write comprehensive tests for new features
- Update documentation for any changes
- Ensure backward compatibility

## 🆘 Support

### Common Issues

#### **Quiz Questions Not Generating**
- Check Gemini API key configuration
- Verify internet connection
- Review Django logs for error details

#### **Evaluation Scores Seem Incorrect**
- Check keyword matching in debug logs
- Verify syllabus content quality
- Review token analysis results

#### **Performance Issues**
- Optimize database queries
- Check AI API rate limits
- Monitor server resources

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check this README and code comments
- **Community**: Join discussions in the repository

## 🔮 Future Enhancements

### Planned Features
- **Multi-language Support**: Internationalization for global use
- **Advanced Analytics**: Machine learning for learning pattern analysis
- **Collaborative Features**: Group quizzes and peer assessments
- **Mobile App**: Native mobile applications
- **Integration APIs**: LMS integration capabilities

### Technical Improvements
- **Microservices Architecture**: Scalable service separation
- **Real-time Features**: WebSocket integration for live quizzes
- **Advanced AI**: Custom fine-tuned models for domain-specific content
- **Performance Optimization**: Caching and database optimization

## 📈 Version History

### v1.0.0 (Current)
- Initial release with core quiz functionality
- Bloom's taxonomy integration
- AI-powered question generation
- Comprehensive feedback system
- Multi-user support

---

**Built with ❤️ for Educational Excellence**

*Empowering education through intelligent assessment*


