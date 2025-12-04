"""Integration tests for request creation workflows."""
import pytest
from website.models import Requests, User
from website import db


class TestUserRequestCreation:
    """Test request creation by regular users (role=0)."""

    def test_user_creates_request_for_themselves(self, client, app, user):
        """Test user can create request for themselves."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
        
        response = client.post('/', data={
            'requested_for_email': user.email,
            'access_level': '1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            request_obj = Requests.query.filter_by(requester_id=user.id).first()
            assert request_obj is not None
            assert request_obj.requested_for_email == user.email
            assert request_obj.access_level == 1
            assert request_obj.state == 0

    def test_user_cannot_create_request_for_others(self, client, app, user, manager):
        """Test user cannot create request for someone else."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
        
        response = client.post('/', data={
            'requested_for_email': manager.email,
            'access_level': '1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Regular Users can only request access for themselves' in response.data


class TestManagerRequestCreation:
    """Test request creation by managers (role=1)."""

    def test_manager_creates_request_for_themselves(self, client, app, manager):
        """Test manager can create request for themselves."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(manager.id)
        
        response = client.post('/', data={
            'requested_for_email': manager.email,
            'access_level': '2'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Request added!' in response.data
        
        with app.app_context():
            request_obj = Requests.query.filter_by(requester_id=manager.id).first()
            assert request_obj is not None
            assert request_obj.requested_for_email == manager.email

    def test_manager_creates_request_for_others(self, client, app, manager, user):
        """Test manager can create request for other users."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(manager.id)
        
        response = client.post('/', data={
            'requested_for_email': user.email,
            'access_level': '1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Request added!' in response.data
        
        with app.app_context():
            request_obj = Requests.query.filter_by(
                requester_id=manager.id,
                requested_for_email=user.email
            ).first()
            assert request_obj is not None


class TestAdminRequestCreation:
    """Test request creation by admins (role=2)."""

    def test_admin_creates_request_for_any_user(self, client, app, admin, user):
        """Test admin can create request for any user."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
        
        response = client.post('/', data={
            'requested_for_email': user.email,
            'access_level': '2'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Request added!' in response.data
        
        with app.app_context():
            request_obj = Requests.query.filter_by(
                requester_id=admin.id,
                requested_for_email=user.email
            ).first()
            assert request_obj is not None
