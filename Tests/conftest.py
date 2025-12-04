import pytest
from werkzeug.security import generate_password_hash
from website import create_app, db
from website.models import User, Requests

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "DB_NAME": ":memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    user = User(email="user@test.com", role=0, first_name="TestUser", 
                password=generate_password_hash('password123', method='pbkdf2:sha256'))
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user

@pytest.fixture
def admin(app):
    admin = User(email="admin@test.com", role=2, first_name="TestAdmin", 
                 password=generate_password_hash('password123', method='pbkdf2:sha256'))
    db.session.add(admin)
    db.session.commit()
    db.session.refresh(admin)
    return admin

@pytest.fixture
def manager(app):
    manager = User(email="manager@test.com", role=1, first_name="TestManager", 
                   password=generate_password_hash('password123', method='pbkdf2:sha256'))
    db.session.add(manager)
    db.session.commit()
    db.session.refresh(manager)
    return manager

@pytest.fixture
def other_user(app):
    other_user = User(email="other@test.com", role=0, first_name="OtherUser", 
                      password=generate_password_hash('password123', method='pbkdf2:sha256'))
    db.session.add(other_user)
    db.session.commit()
    db.session.refresh(other_user)
    return other_user
    
@pytest.fixture
def sample_request(app, manager, user):
    request = Requests(
        requester_id=manager.id,
        requested_for_email=user.email,
        requested_for_id=user.id,
        access_level=1,
        state=0,
        justification="Test request"
    )
    db.session.add(request)
    db.session.commit()
    db.session.refresh(request)
    return request

@pytest.fixture
def Admin_count_one(app):
    admin_count = 1

@pytest.fixture
def Admin_count_two(app):
    admin_count = 2