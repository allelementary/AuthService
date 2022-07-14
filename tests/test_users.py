import pytest
from jose import jwt
from app import schemas
from app.config import settings
# todo write tests on update_user, get_user


def test_root(client):
    res = client.get('/')
    assert res.status_code == 200


def test_create_user(client):
    email = 'hello123@gmail.com'
    password = 'password123'
    res = client.post(
        '/users', json={'email': email, 'password': password})
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == email
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        '/login', data={'username': test_user['email'],
                        'password': test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, [settings.algorithm])
    idx: str = payload.get("user_id")
    assert idx == test_user['id']
    assert login_res.token_type == 'bearer'
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('hello123@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('hello123@gmail.com', None, 422),
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={'username': email, 'password': password})
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "scope, user_scopes, denied_access", [
        (["admin"], ["admin"], False),
        (["admin"], [], True),
    ]
)
def test_update_user_permission(
        test_user, authorized_admin_client,
        scope, user_scopes, denied_access):
    url = f"/update-permission/{test_user['id']}"
    response = authorized_admin_client.patch(url, params={"scope": scope, "denied_access": denied_access})
    user = authorized_admin_client.get(f"/users/{test_user['id']}").json()
    assert response.status_code == 201
    assert user["scopes"] == user_scopes


def test_admin_access(authorized_admin_client):
    response = authorized_admin_client.get("/test-admin-access")
    assert response.status_code == 200
