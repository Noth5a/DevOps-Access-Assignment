# Importing Dependencies
import email
from flask import Blueprint, render_template, request, flash, jsonify  
from flask_login import login_required, current_user 
from .models import Requests, User  
from . import db 
import json  
from datetime import datetime

# Create a Blueprint named 'views' to group related routes
views = Blueprint('views', __name__)

# Route for the home page that handles both GET and POST requests
@views.route('/', methods=['GET', 'POST'])
@login_required 
def home():


    print(current_user.role)

    if current_user.role == 2:
        requests = Requests.query.all()
    elif current_user.role == 1:
        requests = Requests.query.filter_by(requester_id=current_user.id).all()
    else:
        requests = Requests.query.filter_by(requested_for_email=current_user.email).all()

    print("Number of Requests:", len(requests))
    print(f"Requests fetched: {requests}")


    if request.method == 'POST':
        requested_for_email = request.form.get('requested_for_email')
        access_level = request.form.get('access_level')


        if len(requested_for_email) < 1 or len(access_level) < 1:
            flash('Request Name and Issuer are required!', category='error')  # Flash an error message if the Certification is empty
        else:
                
            # Create a new Certification
            new_request = Requests(
                requester_id=current_user.id,
                requested_for_email=requested_for_email,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                access_level=1,
                requested_for_id=None,
                state=0,
                justification="",
            )

            db.session.add(new_request) 
            db.session.commit() 
            flash('Request added!', category='success') 

    # Render the home template and pass the current user object
    return render_template("home.html", user=current_user, requests=requests)

# Update request route
@views.route('/update_request', methods=['PUT','GET'])
def update_request():
        request_id = request.get_json().get('request_id')
        

        requested_for_email = request.get_json().get('requested_for_email')
        last_updated = datetime.now()
        access_level = request.get_json().get('access_level')

        request_obj = Requests.query.get(request_id)

        print("Request ID from Views.Py:", request_id, requested_for_email, last_updated, access_level)

        if not request_obj:
            flash('Request not found!', category = 'error')

        try:
            if requested_for_email: request_obj.requested_for_email = requested_for_email
            if last_updated: request_obj.last_updated = last_updated
            if access_level: request_obj.access_level = access_level

            db.session.commit()  # Save changes
            flash('Request Updated Successfully', category='success')
            return jsonify({}) 

        except Exception as e:
        # If an error occurs, rollback the transaction and log the error
            print(f"Error: {str(e)}")
            db.session.rollback()
            return jsonify({"message": f"Server error: {str(e)}"}), 500  # Return 500 if there is an error

        
@views.route('/Users', methods=['GET'])
def users():
    if current_user.role != 2:
        flash('You must be an Admin to view users', category='error')
        return render_template("home.html", user=current_user)
    else:
        all_users = User.query.all()
        return render_template("Users.html", user=current_user, users=all_users)





# Route to handle note deletion
@views.route('/delete-Request', methods=['POST'])
def delete_Request():
    """
    Route for deleting a note via AJAX.
    - Expects a JSON payload containing the note ID.
    - Deletes the note if it exists and belongs to the current user.
    """
    data = json.loads(request.data)  
    requestId = data.get('requestId')  
    request_obj = Requests.query.get(requestId)  
    if request_obj:
        if current_user.role == 1 : 
            db.session.delete(request_obj)  
            db.session.commit()
            flash('Request deleted.', category = 'success')
        elif current_user.role == 0:
            flash('You must be an Admin to delete', category = 'error')

    return jsonify({})  # Return an empty JSON response to indicate success