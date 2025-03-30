from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Quiz, Subject, Chapter, Question, Option, User, Score
from sqlalchemy.sql import func


bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin Credentials
ADMIN_USERNAME = "sachin"
ADMIN_PASSWORD = "1234"

# Admin Login Route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))

        flash('Invalid credentials!', 'danger')

    return render_template('admin/login.html')

# Admin Logout
@bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

# Admin Dashboard
@bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    questions = Question.query.all()    
    return render_template('admin/dashboard.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)

# admin login reqired
def admin_required():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

# View all subjects
@bp.route('/subjects')
def subjects():
    admin_required()
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

# Add Subject
@bp.route('/add_subject', methods=['POST'])
def add_subject():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    name = request.form.get('name')
    if name:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')

    return redirect(url_for('admin.dashboard'))

# Delete a subject
@bp.route('/subjects/delete/<int:id>')
def delete_subject(id):
    admin_required()
    subject = Subject.query.get(id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted!', 'info')
    return redirect(url_for('admin.dashboard'))

# View all chapters for a subject
@bp.route('/subjects/<int:subject_id>/chapters')
def chapters(subject_id):
    admin_required()
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/chapters.html', subject=subject)

# Add Chapter
@bp.route('/add_chapter', methods=['POST'])
def add_chapter():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    name = request.form.get('name')
    subject_id = request.form.get('subject_id')

    if name and subject_id:
        chapter = Chapter(name=name, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')

    return redirect(url_for('admin.dashboard'))

# Delete a chapter
@bp.route('/chapters/delete/<int:id>')
def delete_chapter(id):
    admin_required()
    chapter = Chapter.query.get(id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted!', 'info')
    return redirect(url_for('admin.dashboard'))

# add new quiz question
@bp.route('/add_question', methods=['POST'])
def add_question():
    try:
        question_text = request.form.get('question_text')
        quiz_id = request.form.get('quiz_id')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')  # e.g., '1' means option1 is correct

        print(f"Received Data: {question_text}, {quiz_id}, {option1}, {option2}, {option3}, {option4}, Correct: {correct_option}")

        # Validate inputs
        if not all([question_text, quiz_id, option1, option2, option3, option4, correct_option]):
            flash("All fields are required!", "error")
            return redirect(url_for('admin.dashboard'))

        try:
            quiz_id = int(quiz_id)
        except ValueError:
            flash("Invalid quiz ID!", "error")
            return redirect(url_for('admin.dashboard'))

        new_question = Question(text=question_text, quiz_id=quiz_id)
        db.session.add(new_question)
        db.session.commit()  

        # Prepare options
        options = [
            Option(text=option1, question_id=new_question.id, is_correct=(correct_option == '1')),
            Option(text=option2, question_id=new_question.id, is_correct=(correct_option == '2')),
            Option(text=option3, question_id=new_question.id, is_correct=(correct_option == '3')),
            Option(text=option4, question_id=new_question.id, is_correct=(correct_option == '4')),
        ]

        db.session.add_all(options)
        db.session.commit()

        print("Question and Options Added Successfully")
        flash("Question added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        flash("An error occurred while adding the question!", "error")

    return redirect(url_for('admin.dashboard'))


@bp.route('/questions/delete/<int:id>')
def delete_question(id):
    admin_required()
    question = Question.query.get(id)
    if question:
        Option.query.filter_by(question_id=question.id).delete()        
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted!', 'info')
    return redirect(url_for('admin.dashboard'))



# Add quiz
@bp.route('/add_quiz', methods=['POST'])
def add_quiz():
    name = request.form.get('title')  
    chapter_id = request.form.get('chapter_id')  
    subject_id = request.form.get('subject_id') 
    print(name, chapter_id, subject_id)

    if not name or not chapter_id or not subject_id:
        return "Quiz name, chapter ID, and subject ID are required", 400 
    
    new_quiz = Quiz(
        name=name,
        chapter_id=int(chapter_id),  
        subject_id=int(subject_id)  
    )
    
    db.session.add(new_quiz)
    db.session.commit()

    return redirect(url_for('admin.dashboard'))


# Delete a quiz
@bp.route('/quizzes/delete/<int:id>')
def delete_quiz(id):
    admin_required()
    quiz = Quiz.query.get(id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted!', 'info')
    return redirect(url_for('admin.dashboard'))

# summery
@bp.route('/summary')
def summary():
    subjects = Subject.query.all()

    # Fetch top scores for each subject
    subject_data = []
    for subject in subjects:
        top_score = (
            db.session.query(func.max(Score.score))
            .join(Quiz, Score.quiz_id == Quiz.id)  
            .filter(Quiz.subject_id == subject.id)  
            .scalar()
        )
        subject_data.append({
            "name": subject.name,
            "top_score": top_score if top_score is not None else 0
        })

    return render_template(
        'admin/summary.html',
        users=User.query.all(),
        subjects=subject_data,
        chapters=Chapter.query.all(),
        quizzes=Quiz.query.all(),
        questions=Question.query.all()
    )
# search 
@bp.route('/search')
def search():
    query = request.args.get('query', '')
    results = []
    
    if query:
        results = User.query.filter((User.username.contains(query)) | (User.email.contains(query))).all() + \
                  Subject.query.filter(Subject.name.contains(query)).all() + \
                  Chapter.query.filter(Chapter.name.contains(query)).all() + \
                  Quiz.query.filter(Quiz.name.contains(query)).all() + \
                  Question.query.filter(Question.text.contains(query)).all()

    return render_template('admin/search.html', results=results)
