# Importing Dependencies
from ast import If
from copy import error
import email
import re
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, current_app  
from flask_login import login_required, current_user
from website.Security import can_delete_user, can_modify_user, is_admin 
from .models import Requests, User  
from . import db 
import json  
from datetime import datetime
from website.Security import can_create_request, can_delete_request, can_view_request, can_update_request, is_admin
from website.State_Transition import get_next_state, allowed_transition


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required 
def home():

    if request.method == 'POST':
        requested_for_email = request.form.get('requested_for_email')
        access_level = request.form.get('access_level')
        
        # Email validation
        EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(EMAIL_REGEX, requested_for_email):
            flash("Invalid email format", category='error')
            current_app.logger.warning(
                f"Invalid email format attempt by user {current_user.id}: {requested_for_email}"
            )
            return redirect(url_for('views.home'))
        
        allowed, reason = can_create_request(current_user, requested_for_email)
        if not allowed:
            flash(reason, category='error')
            current_app.logger.warning(
                f"Unauthorized request creation attempt by user {current_user.id} for email {requested_for_email}"
            )
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
            current_app.logger.info(
                f"Request created by user {current_user.id} for email {requested_for_email}"
            )
            return redirect(url_for('views.home'))
        

        return redirect(url_for('views.home'))


    print(current_user.role)

    if current_user.role == 2:
        requests = Requests.query.all()
    elif current_user.role == 1:
        requests = Requests.query.filter((Requests.requester_id==current_user.id) | (Requests.requested_for_email==current_user.email)).all()
    else:
        requests = Requests.query.filter_by(requested_for_email=current_user.email).all()

    print("Number of Requests:", len(requests))
    print(f"Requests fetched: {requests}")


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
        current_app.logger.warning(
            f"Unauthorized user modification attempt by user {current_user.id} on user {user_id}"
        )
        return jsonify({})
    elif allowed == True:
        old_email = user_obj.email
        old_role = user_obj.role
        user_obj.email = email
        user_obj.role = role
        db.session.commit()
        flash('User updated successfully', category='success')
        current_app.logger.info(
            f"User {user_id} updated by admin {current_user.id}: email changed from {old_email} to {email}, role changed from {old_role} to {role}"
        )
    else:
        flash('Error', category='error')
        current_app.logger.error(
            f"Error occurred during user update by user {current_user.id} on user {user_id}"
        )
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
        original_requested_for_email = request_obj.requested_for_email 


        if len(access_level) < 1:
            flash('Access Level is required!', category='error')  
            return jsonify({})
        elif access_level not in ["0", "1", "2"]:
            flash (f"Invalid access level: {access_level}. Must be one of Viewer, Editor, or Admin.", category='error') 
            current_app.logger.error(
                f"Invalid access level provided by user {current_user.id} for request {request_id}"
            )
            return jsonify({})
            
        elif len(requested_for_email) < 1:
            flash('Requested For Email is required!', category='error')  
            return jsonify({})
        elif len(requested_for_email) > 200: 
            flash('Requested For Email is too long!', category='error')  
            return jsonify({})
        else:
            # Email validation
            EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
            if not re.match(EMAIL_REGEX, requested_for_email):
                flash("Invalid email format", category='error')
                current_app.logger.warning(
                    f"Invalid email format in update request by user {current_user.id}: {requested_for_email}"
                )
                return jsonify({})
            allowed, reason = can_update_request(current_user, original_requested_for_email, requester_id)
            if not allowed:
                flash(reason, category='error')
                current_app.logger.warning(
                    f"Unauthorized request update attempt by user {current_user.id} on request {request_id}"
                )
                return jsonify({})
            elif allowed:
            
                print("Request ID from Views.Py:", request_id, requested_for_email, last_updated, access_level)

                if not request_obj:
                    flash('Request not found!', category = 'error')
                    current_app.logger.error(
                        f"Request {request_id} not found during update attempt by user {current_user.id}"
                    )
                    return jsonify({})

            try:
             if request_obj is None:
                 current_app.logger .info(
                    f"Request {request_id} found for update by user {current_user.id}"
                 )
                 return flash('Request not found!', category='error')
             if requested_for_email: request_obj.requested_for_email = requested_for_email
             if last_updated: request_obj.last_updated = last_updated
             if access_level is not None: request_obj.access_level = access_level

             db.session.commit()  # Save changes
             flash('Request Updated Successfully', category='success')
             current_app.logger.info(
                    f"Request {request_id} updated by user {current_user.id}"
                )
             return jsonify({}) 

            except Exception as e:
             print(f"Error: {str(e)}")
             db.session.rollback()
             return jsonify({"message": f"Server error: {str(e)}"}), 500 

@views.route('/Users', methods=['GET'])
@login_required
def users():
    if not is_admin(current_user):
        flash('Only Admins can view the users list.', category='error')
        current_app.logger.warning(
            f"Unauthorized users list access attempt by user {current_user.id}"
        )
        return redirect(url_for('views.home'))
    
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
        current_app.logger.warning(
            f"Unauthorized user deletion attempt by user {current_user.id} on user {UserId}: {response}"
        )
        return jsonify({})
    elif allowed == True:
        deleted_email = user_obj.email
        deleted_role = user_obj.role
        db.session.delete(user_obj)
        db.session.commit()
        flash('User deleted.', category='success')
        current_app.logger.info(
            f"User {UserId} (email: {deleted_email}, role: {deleted_role}) deleted by admin {current_user.id}"
        )


    else:
        flash('Error', category='error')
        current_app.logger.error(
            f"Error occurred during user deletion by user {current_user.id} on user {UserId}"
        )
    return jsonify({})

@views.route('/updateState', methods=['PUT'])
@login_required
def update_state():
    request_id = request.get_json().get('requestId')
    request_obj = Requests.query.get(request_id)
    current_state = request_obj.state if request_obj else None

    if not is_admin(current_user):
        flash('Only Admins can update the request status.', category='error')
        current_app.logger.warning( 
            f"Unauthorized request state update attempt by user {current_user.id} on request {request_id}"
        )  
        return jsonify({})
    
    # Get the next state in the approval workflow (0->1->2->3)
    next_state = get_next_state(current_state)
    
    # Check if the transition is allowed
    if not allowed_transition(current_state, next_state):
        if current_state == 3:
            flash('Request is already completed.', category='error')
        elif current_state == 4:
            flash('Request has been denied previously.', category='error')
        else:
            flash('Cannot progress from this state.', category='error')
        current_app.logger.error(
            f"Invalid state transition attempt from {current_state} to {next_state} by user {current_user.id} on request {request_id}"
        )
        return jsonify({})
    
    # Apply the state transition
    request_obj.state = next_state
    db.session.commit()
    flash('Request state Updated', category='success')
    current_app.logger.info(
        f"Request {request_id} state updated from {current_state} to {next_state} by user {current_user.id}"
    )
    
    return jsonify({})

@views.route('/Reject', methods = ['PUT'])
@login_required
def Reject():
    request_id = request.get_json().get('requestId')
    request_obj = Requests.query.get(request_id)
    state = request_obj.state if request_obj else None
    
    if not is_admin(current_user):
        flash('Only Admins can update the request status.', category='error')
        current_app.logger.warning( 
            f"Unauthorized request rejection attempt by user {current_user.id} on request {request_id}"
        )
        return jsonify({})
    elif not allowed_transition(state, 4):
        flash("You can not reject from this state.", category='error')
        return jsonify({})
    else:
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
            current_app.logger.warning(
                f"Unauthorized request deletion attempt by user {current_user.id} on request {requestId}: {response}"
            )
        elif allowed:
            deleted_state = request_obj.state
            deleted_email = request_obj.requested_for_email
            db.session.delete(request_obj)  
            db.session.commit()
            flash('Request deleted.', category = 'success')
            current_app.logger.info(
                f"Request {requestId} (for: {deleted_email}, state: {deleted_state}) deleted by user {current_user.id}"
            )
    else:
        flash('Request not found.', category='error')
        current_app.logger.error(
            f"Request {requestId} not found during deletion attempt by user {current_user.id}"
        )

    return jsonify({}) 