import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_session, Base, DB_URI
from app.oauth2 import create_access_token
from tests.test_data import users

SQLALCHEMY_DATABASE_URL_TEST = f'{DB_URI}_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL_TEST)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print('Create database')
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(session):
    def override_get_db():
        print('Overwrite database')
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_db
    yield TestClient(app)


@pytest.fixture(scope="session")
def test_user(client):
    user_data = {'email': users[0].email, 'password': users[0].password}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture(scope="session")
def test_user2(client):
    user_data = {'email': users[1].email, 'password': users[1].password}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture(scope="session")
def test_admin(client):
    user_data = {
        'email': users[2].email,
        'password': users[2].password,
        'scopes': users[2].scopes
    }
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_admin = res.json()
    new_admin['password'] = user_data['password']
    return new_admin


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def admin_token(test_admin):
    return create_access_token({"user_id": test_admin["id"], "scopes": ["admin"]})


@pytest.fixture
def authorized_admin_client(client, admin_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {admin_token}"
    }
    return client
