from website.models import User
from website.Security import can_delete_user, can_modify_user, is_admin

def test_can_delete_admin():
    user = User(id=1, role=2)  # Admin user
    target_user = User(id=2, role=2)  # Regular user
    admin_count = 2
    assert can_delete_user(user, target_user, admin_count) == (True, '')

def test_cannot_delete_last_admin():
    user = User(id=1, role=2)  # Admin user
    target_user = User(id=2, role=2)  # Regular user
    admin_count = 1
    assert can_delete_user(user, target_user, admin_count) == (False, 'Cannot delete the last Admin user.')

def test_cannot_delete_self():
    user = User(id=1, role=2)  # Admin user
    target_user = User(id=1, role=2)  # Same user
    admin_count = 2
    assert can_delete_user(user, target_user, admin_count) == (False, 'You cannot delete your own account.')
