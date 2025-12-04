# Importing Dependencies
import os
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from os import path 
from flask_login import LoginManager 
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import os


csrf = CSRFProtect()


db = SQLAlchemy()

def create_app(test_config=None):

    app = Flask(__name__)
    #Back-Up Variables set incase of errors, In a production environment these would not be set.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL","sqlite:///dev.db")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    if test_config:

        app.config.update(test_config)
        
    if not app.config.get("TESTING"):  
        if app.config["SECRET_KEY"] == "dev-secret-key":
            raise RuntimeError("SECRET_KEY must be set in production!")
        if "sqlite:///dev.db" in app.config["SQLALCHEMY_DATABASE_URI"]:
            raise RuntimeError("DATABASE_URL must be set in production!")
    

    db.init_app(app)

    csrf.init_app(app)

    # Only configure file logging if not in test mode
    if not app.config.get('TESTING'):
        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = RotatingFileHandler(
            "logs/app.log",
            maxBytes=10240,   # 10KB per file before rotation
            backupCount=5     # keep 5 old logs
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Application startup")
    else:
        # In test mode, just use console logging
        app.logger.setLevel(logging.INFO)

    from .views import views 
    from .auth import auth 


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') 


    from .models import User, Requests

    # Create the database if it doesn't exist yet
    with app.app_context():
        db.create_all() 
        print('Created Database!')


    login_manager = LoginManager()
    

    login_manager.login_view = 'auth.login'
    

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))  

    return app 