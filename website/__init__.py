# Importing Dependencies
import os
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from os import path 
from flask_login import LoginManager 
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


db = SQLAlchemy()

def create_app(test_config=None):

    app = Flask(__name__)
    
    DB_NAME = os.environ.get("DATABASE_NAME")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    if test_config:

        app.config.update(test_config)
    else:

        DB_NAME = os.environ.get("DATABASE_NAME")
        SECRET_KEY = os.environ.get("SECRET_KEY")
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['SECRET_KEY'] = SECRET_KEY
    

    db.init_app(app)

    csrf.init_app(app)


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