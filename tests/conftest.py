from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_session, Base
from app.config import settings
from app.oauth2 import create_access_token
from app import models
from alembic import command, config as alembic_config
import pytest

# TODO finish db
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@' \
                          f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='session', autouse=True)
def db_session(prepare_config):
    from app.config import settings as config
    from app.database import create_db, drop_db, finish_database_preparation, get_session

    drop_db(SQLALCHEMY_DATABASE_URL, config.database_name)
    create_db(SQLALCHEMY_DATABASE_URL, config.database_name)
    finish_database_preparation(config.DB_DSN_TEST)

    alembic_conf = alembic_config.Config('alembic.ini')
    alembic_conf.set_section_option(
        'alembic', 'sqlalchemy.url', config.DB_DSN_TEST)
    print(f' Upgrading database {config.DB_DSN_TEST}')
    command.upgrade(alembic_conf, 'head')

    yield get_session()


# @pytest.fixture(scope="session")
# def session():
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     print('Create database')
#     db = TestingSessionLocal()
#
#     try:
#         yield db
#     finally:
#         db.close()


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
    user_data = {'email': 'hello123@gmail.com', 'password': 'password123'}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture(scope="session")
def test_user2(client):
    user_data = {'email': 'hello321@gmail.com', 'password': 'password123'}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture(scope="session")
def test_trader(client):
    user_data = {'email': 'hello123@gmail.com', 'password': 'password123',
                 'scopes': ['trade']}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_admin = res.json()
    new_admin['password'] = user_data['password']
    return new_admin


@pytest.fixture(scope="session")
def test_admin(client):
    user_data = {'email': 'hello123@gmail.com', 'password': 'password123',
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
