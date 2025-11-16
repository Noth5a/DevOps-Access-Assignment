# Importing Dependencies
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from os import path 
from flask_login import LoginManager 

# Initialize the database object
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    # Initialize the Flask application
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'jhdfh'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Initialize the database with the Flask app
    db.init_app(app)

    # Import and register the Blueprints for different routes
    from .views import views 
    from .auth import auth 

    # Register the blueprints with URL prefixes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') 


    from .models import User, Requests

    # Create the database if it doesn't exist yet
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all() 
            print('Created Database!')

    # Initialize the LoginManager for managing user sessions
    login_manager = LoginManager()
    
    # Define the login route to redirect unauthenticated users
    login_manager.login_view = 'auth.login'
    
    # Bind the LoginManager instance to the Flask app
    login_manager.init_app(app)

    # Define a function to load a user from the database by their ID (required by Flask-Login)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))  

    return app 