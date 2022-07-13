from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_session, Base, SQLALCHEMY_DATABASE_URL, SQL_URL
from app.config import settings
from app.oauth2 import create_access_token
from app import models
from alembic import command, config as alembic_config
import pytest

# TODO finish db
SQLALCHEMY_DATABASE_URL_TEST = f'{SQLALCHEMY_DATABASE_URL}_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL_TEST)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print('Create database')
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        print('Overwrite database')
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    user_data = {'email': 'hello1234@gmail.com', 'password': 'password123'}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture()
def test_user2(client):
    user_data = {'email': 'hello321@gmail.com', 'password': 'password123'}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture()
def test_trader(client):
    user_data = {'email': 'hello1235@gmail.com', 'password': 'password123',
                 'scopes': ['trade']}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_admin = res.json()
    new_admin['password'] = user_data['password']
    return new_admin


@pytest.fixture()
def test_admin(client):
    user_data = {'email': 'hello1230@gmail.com', 'password': 'password123',
                 'scopes': ['trade', 'admin']}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_admin = res.json()
    new_admin['password'] = user_data['password']
    return new_admin


@pytest.fixture()
def test_trade_access(client):
    user_data = {'email': 'hello123@gmail.com', 'password': 'password123'}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


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
def trade_token(test_trader):
    return create_access_token({"user_id": test_trader["id"], "scopes": ["trade"]})


@pytest.fixture
def authorized_trade_client(client, trade_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {trade_token}"
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


# @pytest.fixture
# def test_posts(test_user, session, test_user2):
#     posts_data = [{
#         "title": "first_title",
#         "content": "first_content",
#         "owner_id": test_user['id']
#     }, {
#         "title": "2nd_title",
#         "content": "2nd_content",
#         "owner_id": test_user['id']
#     }, {
#         "title": "3rd_title",
#         "content": "3rd_content",
#         "owner_id": test_user['id']
#     }, {
#         "title": "3rd_title",
#         "content": "3rd_content",
#         "owner_id": test_user2['id']
#     }]
#
#     def create_post_model(post):
#         return models.Post(**post)
#
#     post_map = map(create_post_model, posts_data)
#     posts = list(post_map)
#
#     session.add_all(posts)
#     session.commit()
#     posts = session.query(models.Post).all()
#     return posts
