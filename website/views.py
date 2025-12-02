# Importing Dependencies
from ast import If
from copy import error
import email
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for  
from flask_login import login_required, current_user

from website.Security import can_delete_user, can_modify_user, is_admin 
from .models import Requests, User  
from . import db 
import json  
from datetime import datetime
from website.Security import can_create_request, can_delete_request, can_view_request, can_update_request, is_admin
from website.State_Transition import get_next_state, allowed_transition

# Create a Blueprint named 'views' to group related routes
views = Blueprint('views', __name__)

# Route for the home page that handles both GET and POST requests
@views.route('/', methods=['GET', 'POST'])
@login_required 
def home():

    if request.method == 'POST':
        requested_for_email = request.form.get('requested_for_email')
        access_level = request.form.get('access_level')
        
        allowed, reason = can_create_request(current_user, requested_for_email)
        if not allowed:
            flash(reason, category='error')
        elif allowed:
            # Create a new request
            new_request = Requests(
                requester_id=current_user.id,
                requested_for_email=requested_for_email,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                access_level=access_level,
                requested_for_id=User.query.filter_by(email=requested_for_email).first().id if User.query.filter_by(email=requested_for_email).first() else None, 
                state=0,
                justification="",
            )

            db.session.add(new_request) 
            db.session.commit() 
            flash('Request added!', category='success')
            return redirect(url_for('views.home'))
        
        # Redirect after POST to prevent form resubmission
        return redirect(url_for('views.home'))

    # Query requests for GET requests
    print(current_user.role)

    if current_user.role == 2:
        requests = Requests.query.all()
    elif current_user.role == 1:
        requests = Requests.query.filter((Requests.requester_id==current_user.id) | (Requests.requested_for_email==current_user.email)).all()
    else:
        requests = Requests.query.filter_by(requested_for_email=current_user.email).all()

    print("Number of Requests:", len(requests))
    print(f"Requests fetched: {requests}")

    # Render the home template and pass the current user object
    return render_template("home.html", user=current_user, requests=requests)


@views.route('/update_user', methods=['PUT','GET'])
@login_required
def update_user():
    user_id = request.get_json().get('user_id')
    email = request.get_json().get('email')
    role = request.get_json().get('role')
    user_obj = User.query.get(user_id)
    admin_count = User.query.filter_by(role=2).count()
    allowed , response = can_modify_user(current_user, user_obj, admin_count)

    if len(email) < 1:
        flash('Email is required!', category='error')
    elif len(email) > 200:
        flash('Email is too long!', category='error')
    elif allowed == False:
        flash(response, category='error')
        return jsonify({})
    elif allowed == True:
        user_obj.email = email
        user_obj.role = role
        db.session.commit()
        flash('User updated successfully', category='success')
    else:
        flash('Error', category='error')
    return jsonify({})


# Update request route
@views.route('/update_request', methods=['PUT','GET'])
@login_required
def update_request():
        
        print(current_user.role)
    
        if current_user.role == 2:
            requests = Requests.query.all()
        elif current_user.role == 1:
         requests = Requests.query.filter((Requests.requester_id==current_user.id) | (Requests.requested_for_email==current_user.email)).all()
        else:
         requests = Requests.query.filter_by(requested_for_email=current_user.email).all()

        request_id = request.get_json().get('request_id')
        

        requested_for_email = request.get_json().get('requested_for_email')
        last_updated = datetime.now()
        access_level = request.get_json().get('access_level')
        request_obj = Requests.query.get(request_id)
        requester_id = request_obj.requester_id


        if len(access_level) < 1:
            flash('Access Level is required!', category='error')  # Flash an error message
            return jsonify({})
        elif access_level not in ["0", "1", "2"]:
            flash (f"Invalid access level: {access_level}. Must be one of Viewer, Editor, or Admin.", category='error')  # Flash an error message
            return jsonify({})
        elif len(requested_for_email) < 1:
            flash('Requested For Email is required!', category='error')  # Flash an error message
            return jsonify({})
        elif len(requested_for_email) > 200: 
            flash('Requested For Email is too long!', category='error')  # Flash an error message
            return jsonify({})
        else:
            allowed, reason = can_update_request(current_user, requested_for_email, requester_id)
            if not allowed:
                flash(reason, category='error')
                return jsonify({})
            elif allowed:
            
                print("Request ID from Views.Py:", request_id, requested_for_email, last_updated, access_level)

                if not request_obj:
                    flash('Request not found!', category = 'error')

            try:
             if requested_for_email: request_obj.requested_for_email = requested_for_email
             if last_updated: request_obj.last_updated = last_updated
             if access_level is not None: request_obj.access_level = access_level

             db.session.commit()  # Save changes
             flash('Request Updated Successfully', category='success')
             return jsonify({}) 

            except Exception as e:
         # If an error occurs, rollback the transaction and log the error
             print(f"Error: {str(e)}")
             db.session.rollback()
             return jsonify({"message": f"Server error: {str(e)}"}), 500  # Return 500 if there is an error

@views.route('/Users', methods=['GET'])
@login_required
def users():
    if is_admin(current_user, None) == False:
        flash('Only Admins can view the users list.', category='error')
        return redirect(url_for('views.home'))
    elif is_admin(current_user, None) == True:
        all_users = User.query.all()
        return render_template("Users.html", user=current_user, users=all_users)

@views.route('/deleteUser', methods=['POST'])
@login_required
def deleteUser():
    UserId = request.get_json().get('userId')
    user_obj = User.query.get(UserId)
    admin_count = User.query.filter_by(role=2).count()

    allowed , response = can_delete_user(current_user, user_obj, admin_count)

    if allowed == False:
        flash(response, category='error')
        return jsonify({})
    elif allowed == True:
        db.session.delete(user_obj)
        db.session.commit()
        flash('User deleted.', category='success')
    else:
        flash('Error', category='error')
    return jsonify({})

@views.route('/updateState', methods=['PUT'])
@login_required
def update_state():
    request_id = request.get_json().get('requestId')
    request_obj = Requests.query.get(request_id)
    state = request_obj.state if request_obj else None

    if is_admin(current_user, None) == False:
        flash('Only Admins can update the request status.', category='error')
    elif state == 0:
        request_obj.state = 1
        db.session.commit()
        flash('Request state Updated', category='success') 
    elif state == 1:
        request_obj.state = 2
        db.session.commit()
        flash('Request state Updated', category='success')
    elif state == 2:
        request_obj.state = 3
        db.session.commit()
        flash('Request state Updated', category='success')
    elif state == 3:
        flash('Request is already completed.', category='error')
    elif state == 4:
        flash('Request has been denied previously.', category='error')
    else :
        flash('Invalid state value.', category='error')
    return jsonify({})

@views.route('/Reject', methods = ['PUT'])
@login_required
def Reject():
    request_id = request.get_json().get('requestId')
    request_obj = Requests.query.get(request_id)
    state = request_obj.state if request_obj else None
    if is_admin(current_user, None) == False:
        flash('Only Admins can update the request status.', category='error')
        return jsonify({})
    elif allowed_transition(state, 4)==False:
        flash("You can not reject from this state.", category='error')
        return jsonify({})
    elif allowed_transition(state, 4)==True:
        request_obj.state = 4
        db.session.commit()
        flash('Request rejected', category='sucess')
        return redirect(url_for('views.home'))

# Route to handle note deletion
@views.route('/delete-Request', methods=['POST'])
@login_required
def delete_Request():
    """
    Route for deleting a note via AJAX.
    - Expects a JSON payload containing the note ID.
    - Deletes the note if it exists and belongs to the current user.
    """
    data = json.loads(request.data)  
    requestId = data.get('requestId')  
    request_obj = Requests.query.get(requestId)  
    requester_id = request_obj.requester_id if request_obj else None
    if request_obj:
        allowed, response = can_delete_request(current_user, requestId, requester_id )
        if not allowed:
            flash(response, category = 'error')
        elif allowed: 
            db.session.delete(request_obj)  
            db.session.commit()
            flash('Request deleted.', category = 'success')

    return jsonify({})  # Return an empty JSON response to indicate success