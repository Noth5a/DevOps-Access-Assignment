"""Integration tests for authentication workflows."""
import pytest
from website.models import User
from website import db


class TestUserSignup:
    """Test user registration workflows."""

    def test_user_signs_up_with_role_0(self, client, app):
        """Test regular user signup (role=0)."""
        response = client.post('/sign-up', data={
            'email': 'testuser@example.com',
            'firstName': 'TestUser',
            'password1': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.filter_by(email='testuser@example.com').first()
            assert user is not None
            assert user.role == 0
            assert user.first_name == 'TestUser'

    def test_manager_signs_up_with_role_1(self, client, app):
        """Test manager signup (role=1)."""
        response = client.post('/sign-up', data={
            'email': 'manager@example.com',
            'firstName': 'TestManager',
            'password1': 'password123',
            'password2': 'password123',
            'role': 'on' 
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.filter_by(email='manager@example.com').first()
            assert user is not None
            assert user.role == 1
            assert user.first_name == 'TestManager'


class TestLoginLogout:
    """Test login and logout workflows."""

    def test_user_can_login(self, client, user):
        """Test user can login with correct credentials."""
        response = client.post('/login', data={
            'email': user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Logged in successfully' in response.data

    def test_user_cannot_login_with_wrong_password(self, client, user):
        """Test user cannot login with incorrect password."""
        response = client.post('/login', data={
            'email': user.email,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Incorrect password' in response.data

    def test_user_cannot_login_with_nonexistent_email(self, client):
        """Test user cannot login with non-existent email."""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email does not exist' in response.data

    def test_user_can_logout(self, client, user):
        """Test user can logout."""
        # Login first
        client.post('/login', data={
            'email': user.email,
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200

        assert b'Login' in response.data
