from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db  
from models import User, Quiz, Score, Question, Option, Subject, Chapter
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

bp = Blueprint('user', __name__, url_prefix='/user')

def load_user(user_id):
    return User.query.get(int(user_id))


# regiser user
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') 

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('user.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('user.register'))

        
        new_user = User(username=username, email=email, password=password, full_name=full_name)
        db.session.add(new_user)
        db.session.commit()

        flash(' User registered successfully! Please login.', 'success')
        return redirect(url_for('user.login'))

    return render_template('register.html')

# login user
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard', user_id=user.id)) 
        else:
            flash('Invalid credentials! Try again.', 'danger')

    return render_template('login.html')

# logout user
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(' Logged out successfully!', 'info')
    return redirect(url_for('user.login'))

#user dashboard
@bp.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    quizzes = Quiz.query.all()
    scores = Score.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', quizzes=quizzes, scores=scores, user_id=user_id)

# take quiz
# submit quiz 
@bp.route('/quiz/<int:quiz_id>/attempt/<int:user_id>', methods=['GET', 'POST'])
def quiz_attempt(quiz_id, user_id):  
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        user_answers = {}
        for question in questions:
            user_answers[question.id] = int(request.form.get(str(question.id)))
        return "Quiz Submitted!"
    return render_template('quiz_attempt.html', quiz=quiz, questions=questions, user_id=user_id) 


# submit quiz
from models import db, Question, Option, Score
@bp.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    data = request.form
    user_id = data.get('user_id')
    quiz_id = data.get('quiz_id')

    if not user_id or not quiz_id:
        return jsonify({"error": "User ID or Quiz ID is missing!"}), 400

    try:
        user_id = int(user_id)
        quiz_id = int(quiz_id)
    except ValueError:
        return jsonify({"error": "Invalid User ID or Quiz ID!"}), 400

    #Extract question IDs from form data
    question_ids = []

    for key in data.keys():
        if key.startswith('question_'):
            parts = key.split('_')
            if parts[1].isdigit():
                question_ids.append(int(parts[1]))


    if not question_ids:
        return jsonify({"error": "No valid questions found in the submission!"}), 400

    #Fetch correct answers from the database (store option.id)
    correct_answers_map = {
        option.question_id: option.id
        for option in Option.query.filter(Option.question_id.in_(question_ids), Option.is_correct == True).all()
    }

    #Calculate total questions and correct answers
    total_questions = len(question_ids)
    correct_answers = sum(
        1 for key, user_answer in data.items()
        if key.startswith('question_') and correct_answers_map.get(int(key.split('_')[1])) == int(user_answer)  # ✅ Compare option IDs as integers
    )

    #Calculate score
    score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0

    print(f"[INFO] User ID: {user_id}, Quiz ID: {quiz_id}, Total: {total_questions}, Correct: {correct_answers}, Score: {score}%")

    try:
        new_score = Score(
            user_id=user_id,
            quiz_id=quiz_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score=score
        )
        db.session.add(new_score)
        db.session.commit()

        return jsonify({
            "message": "Quiz submitted successfully!",
            "score": score,
            "total_questions": total_questions,
            "correct_answers": correct_answers
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: Unable to submit quiz"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# user summary
@bp.route('/summary/<int:user_id>')
def user_summary(user_id):
    # Fetch all scores for the user
    scores = Score.query.filter_by(user_id=user_id).all()

    print(f"[DEBUG] Fetching summary for user: {user_id}, Total quizzes found: {len(scores)}")

    if not scores:
        return render_template("summary.html", user_id=user_id, scores=[], summary_data={})

    # Calculate summary stats
    total_quizzes = len(scores)
    avg_score = round(sum(score.score for score in scores) / total_quizzes, 2) if total_quizzes > 0 else 0
    highest_score = max(score.score for score in scores) if scores else 0
    last_quiz = scores[-1] if scores else None

    summary_data = {
        "total_quizzes": total_quizzes,
        "avg_score": avg_score,
        "highest_score": highest_score,
        "last_quiz": last_quiz,
    }

    # Fetch quiz names
    scores_with_names = [
        {
            "quiz_name": score.quiz.name,
            "total_questions": score.total_questions,
            "correct_answers": score.correct_answers,
            "score": score.score
        }
        for score in scores
    ]

    return render_template("summary.html", user_id=user_id, scores=scores_with_names, summary_data=summary_data)


# search quiz page
@bp.route('/search')
def search_quiz_page():
    return render_template('search.html', quizzes=[], search_query="")


@bp.route('/search_quiz', methods=['GET'])
def search_quiz():
    search_query = request.args.get('search', '').strip()

    if not search_query:
        return render_template("search.html", quizzes=[], search_query="")  

    # Search for quizzes based on subject or chapter name
    quizzes = Quiz.query.join(Subject).join(Chapter).filter(
        (func.lower(Subject.name).ilike(f"%{search_query.lower()}%")) |
        (func.lower(Chapter.name).ilike(f"%{search_query.lower()}%"))
    ).all()

    return render_template("search.html", quizzes=quizzes, search_query=search_query)