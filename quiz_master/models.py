from extensions import db  
from flask_login import UserMixin

class User(db.Model,UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password, full_name): 
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name 


class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Relationship to chapters (One Subject has Many Chapters)
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", lazy=True)
    quizzes = db.relationship('Quiz', backref='subject', lazy=True)
    def __repr__(self):
        return f"<Subject {self.name}>"

class Chapter(db.Model):
    __tablename__ = "chapter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    # Relationship to quizzes (One Chapter has Many Quizzes)
    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan", lazy=True)
    def __repr__(self):
        return f"<Chapter {self.name}>"

class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    quiz = db.relationship('Quiz', backref='questions')
    options = db.relationship('Option', backref='question', lazy=True)


class Score(db.Model):
    __tablename__ = "score"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)  
    correct_answers = db.Column(db.Integer, nullable=False)  
    score = db.Column(db.Integer, nullable=False)
    quiz = db.relationship('Quiz', backref='scores') 

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)  # True if this is the correct answer
