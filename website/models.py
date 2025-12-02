# Importing Dependencies
from . import db
from flask_login import UserMixin 
from sqlalchemy.sql import func 



# Setting up the Requests Table
class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_for_email = db.Column(db.String(150), nullable=False)
    requested_for_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    access_level = db.Column(db.Integer, nullable=False) #1Viewer, 2 Editor, 3Authoriser
    state = db.Column(db.Integer, nullable=False, default= 0) # 0 Not Started, 1 Access Requested, 2, Teams requested, 3 Access Granted, 4 Access Denied
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    justification = db.Column(db.String(500), nullable=True)
    teams = db.Column(db.String(300), nullable=True)


 
    # Relationships to fetch User objects
    requester = db.relationship('User', foreign_keys =[requester_id])



# Setting up the User Table
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)  # Primary key column (unique identifier)
    email = db.Column(db.String(150), unique=True) 
    password = db.Column(db.String(150))  
    first_name = db.Column(db.String(150)) 
    last_name = db.Column(db.String(150))
    role = db.Column(db.Integer, nullable=False, default= 0) # 0 User, 1 Requester, 2 Admin
   