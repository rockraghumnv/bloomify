# Bloomify

Bloomify is a smart learning platform that generates quizzes and feedback based on Bloom's Taxonomy, using AI-powered question generation. It supports both teachers and students with tailored portals and analytics.

## Features
- Teacher portal: Upload syllabus, generate smart quizzes
- Student portal: Take quizzes, receive detailed feedback
- Dynamic quiz logic using Bloom's Taxonomy
- AI-powered question generation (Gemini/Gemini Pro)
- Custom authentication and registration for teachers and students
- Feedback and results analysis

## Tech Stack
- Python 3.13+
- Django 5.2+
- google-generativeai (Gemini)
- Bootstrap (for UI)

## Setup
1. Clone the repo:
   ```
   git clone https://github.com/rockraghumnv/bloomify.git
   cd bloomify
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with your secrets:
   ```
   secret_key=your-django-secret-key
   DEBUG=True
   API_KEY=your-google-generativeai-key
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Start the server:
   ```
   python manage.py runserver
   ```

## Usage
- Visit `/` for the main landing page.
- Teachers: Register/login and access `/teachers/` to upload syllabus and create quizzes.
- Students: Register/login and access `/students/` to take quizzes and view feedback.

## Project Structure
- `bloomify/` - Main Django project settings and URLs
- `accounts/` - Custom authentication and registration
- `teachers/` - Teacher portal, syllabus, quiz creation
- `students/` - Student portal, quiz taking, results
- `feedback/` - Feedback and analytics
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS)

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.


