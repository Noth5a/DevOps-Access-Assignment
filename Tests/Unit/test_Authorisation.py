from website.Security import can_create_request, can_delete_request, can_view_request, can_update_request, is_admin
from website.models import User, db

def tes_is_admin(admin):
    assert is_admin(admin, None)

def test_can_view_request_as_admin(admin, sample_request):
    assert can_view_request(admin, sample_request)

def test_can_view_request_as_requester(manager, sample_request):
    assert can_view_request(manager, sample_request)

def test_can_view_request_as_requested_user(user, sample_request):
    assert can_view_request(user, sample_request)

def test_cannot_view_request_as_other_user(app, other_user, sample_request):
     allowed, reason = can_view_request(other_user, sample_request)
     assert not allowed

def test_can_modify_request_as_admin(admin, sample_request):
    assert can_update_request(admin, sample_request, sample_request.requester_id)

def test_can_modify_request_as_requester(manager, sample_request):
    assert can_update_request(manager, sample_request, sample_request.requester_id)

def test_can_modify_request_as_requested_user(user, sample_request):
    assert can_update_request(user, sample_request, sample_request.requester_id)

def test_cannot_modify_request_as_other_user(app, other_user, sample_request):
    allowed , reason = can_update_request(other_user, sample_request, sample_request.requester_id)
    assert not allowed

def test_cannot_delete_request_as_regular_user(user, sample_request):
     allowed, reason = can_delete_request(user, sample_request, sample_request.requester_id)
     assert not allowed

def test_can_delete_request_as_requester(manager, sample_request):
    allowed, reason = can_delete_request(manager, sample_request, sample_request.requester_id)
    assert allowed

def test_can_delete_request_as_admin(admin, sample_request):
    allowed, reason = can_delete_request(admin, sample_request, sample_request.requester_id)
    assert allowed

def test_cannot_delete_request_as_other_user(app, other_user, sample_request):
    allowed, reason = can_delete_request(other_user, sample_request, sample_request.requester_id)
    assert not allowed

def test_can_create_request_as_regular_user(user):
    assert can_create_request(user, user.email)

def test_cannot_create_request_as_regular_user_for_other(other_user, sample_request):
    allowed, reason = can_create_request(other_user, sample_request.requested_for_email)
    assert not allowed

def test_can_create_request_as_manager(manager, user):
    assert can_create_request(manager, user.email)

def test_can_create_request_as_admin(admin, user):
    assert can_create_request(admin, user.email)





