from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from extensions import db

# Import blueprints
from routes.admin import bp as admin_bp
from routes.user import bp as user_bp, load_user

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

# Home Page Route
@app.route('/')
def home():
    return render_template('index.html')

# Set user loader inside app
login_manager.user_loader(load_user)

# Create tables inside application context
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(debug=True)
