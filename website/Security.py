from flask_login import current_user
from website.models import User, Requests


def is_admin(user: User) -> bool:
    """Check if the user is an admin."""
    return user.role == 2
    
def can_delete_request (user: User, request: Requests, requester_id) -> bool:
    if user.role == 0:
            return False, 'You must be an Admin to delete'
    if user.role == 1 and requester_id !=user.id:
            return False, 'Requesters can only delete their own requests.'
    if (user.role == 1 and requester_id == user.id) or (user.role == 2 ): 
            return True, ''
    return False, 'Unauthorized action.'

def can_create_request (user: User, requested_for_email, ) -> bool:
    if user.role == 0 and requested_for_email != user.email:
            return False, 'Regular Users can only request access for themselves.'
    if user.role in [1,2]:
            return True, ''
    if user.role ==0 and requested_for_email == user.email:
            return True, ''
    return False, 'Unauthorized action.'

def can_update_request (user: User, requested_for_email, requester_id) -> bool:
      
      if user.role == 0 and requested_for_email != user.email:
            return False, 'Regular Users can only update their own requests.'
      if user.role == 1 and (requester_id != user.id and requested_for_email != user.email):
                  return False, 'Managers can only update requests they created or that are for them.'
      if user.role not in [0,1,2]:
        return False, 'Unauthorized action.'
      else:
        return True, ''  
      
def can_view_request (user: User, request: Requests) -> bool:
    if user.role == 2:
            return True
    if request.requester_id==user.id:
            return True
    
    if request.requested_for_email==user.email:
            return True, ''
    else:
        return False, 'Unauthorized action.'

def can_delete_user(user: User, target_user: User, admin_count: int) -> tuple[bool, str]:
    """Check if the user can delete the target user."""
    if not is_admin(user):
        return False, 'You must be an Admin to delete users'
    elif target_user is None:
        return False, 'Error, User doesnt exist'
    elif target_user.role == 2 and admin_count <= 1:
        return False, 'Cannot delete the last Admin user.'
    elif user.id == target_user.id:
        return False, 'You cannot delete your own account.'
    elif (is_admin(target_user)==False or admin_count > 1) and user.id != target_user.id:
        return True, ''
    else:
        return False, 'Error'

def can_modify_user(user: User, target_user: User, admin_count: int) -> tuple[bool, str]:
    """Check if the user can modify the target user."""
    if not is_admin(user):
        return False, 'You must be an Admin to modify users'
    elif target_user is None:
        return False, 'Error, User doesnt exist'
    elif user.id == target_user.id:
        return False, 'You cannot modify your own account.'
    elif target_user.role == 2 and admin_count <= 1:
        return False, 'Cannot demote the last Admin user.'
    elif (is_admin(target_user)==False or admin_count > 1) and user.id != target_user.id:
        return True, ''
    else:
        return False, 'Error'