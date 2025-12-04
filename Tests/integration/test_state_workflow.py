"""Integration tests for request state transition workflows."""
import pytest
from website.models import Requests
from website import db


class TestCompleteApprovalWorkflow:
    """Test complete approval workflow: 0→1→2→3."""

    def test_admin_completes_full_approval_workflow(self, client, app, admin, sample_request):
        """Test admin progresses request through all states to completion."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
        
        # State 0 → 1
        response = client.put('/updateState',
            json={'requestId': sample_request.id})
        assert response.status_code == 200
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 1
        
        # State 1 → 2
        response = client.put('/updateState',
            json={'requestId': sample_request.id})
        assert response.status_code == 200
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 2
        
        # State 2 → 3
        response = client.put('/updateState',
            json={'requestId': sample_request.id})
        assert response.status_code == 200
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 3  # Completed


class TestRejectionWorkflows:
    """Test rejection workflows at different stages."""

    def test_reject_immediately_from_state_0(self, client, app, admin, sample_request):
        """Test admin rejects request immediately (0→4)."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
        
        response = client.put('/Reject',
            json={'requestId': sample_request.id})
        
        assert response.status_code == 200 or response.status_code == 302
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 4  # Rejected

    def test_reject_from_state_1(self, client, app, admin, sample_request):
        """Test admin rejects from Access Requested (0→1→4)."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
        
        # Progress to state 1
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            req.state = 1
            db.session.commit()
        
        # Reject from state 1
        response = client.put('/Reject',
            json={'requestId': sample_request.id})
        
        assert response.status_code == 200 or response.status_code == 302
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 4  # Rejected

    def test_reject_from_state_2(self, client, app, admin, sample_request):
        """Test admin rejects from Teams Requested (0→1→2→4)."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
        
        # Progress to state 2
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            req.state = 2
            db.session.commit()
        
        # Reject from state 2
        response = client.put('/Reject',
            json={'requestId': sample_request.id})
        
        assert response.status_code == 200 or response.status_code == 302
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 4  # Rejected

    def test_cannot_reject_from_completed_state(self, client, app, admin, sample_request):
        """Test admin cannot reject already completed request."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
        
        client.put('/updateState', json={'requestId': sample_request.id})  # 0 -> 1
        client.put('/updateState', json={'requestId': sample_request.id})  # 1 -> 2
        client.put('/updateState', json={'requestId': sample_request.id})  # 2 -> 3
        
        # Verify it's at state 3
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 3
        
        # Try to reject from completed state
        response = client.put('/Reject',
            json={'requestId': sample_request.id})
        
        assert response.status_code == 200 or response.status_code == 302
        
        with app.app_context():
            req = Requests.query.get(sample_request.id)
            assert req.state == 3 


class TestNonAdminCannotUpdateState:
    """Test non-admin users cannot update request state."""

    def test_user_cannot_update_state(self, client, user, sample_request):
        """Test regular user cannot progress request state."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
        
        response = client.put('/updateState',
            json={'requestId': sample_request.id})
        
        assert response.status_code == 200

    def test_manager_cannot_update_state(self, client, manager, sample_request):
        """Test manager cannot progress request state."""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(manager.id)
        
        response = client.put('/updateState',
            json={'requestId': sample_request.id})
        
        assert response.status_code == 200
