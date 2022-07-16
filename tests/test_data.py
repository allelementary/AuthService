from app import models

users = [
    models.User(
        email="hello1234@gmail.com",
        password="password123",
        scopes=None,
    ),
    models.User(
        email="hello321@gmail.com",
        password="password123",
        scopes=None,
    ),
    models.User(
        email="hello1230@gmail.com",
        password="password123",
        scopes=['admin'],
    ),
    models.User(
        email="edited123@gmail.com",
        password="edited1234",
        scopes=None,
    ),
    models.User(
        email="hello123@gmail.com",
        password="password123",
        scopes=None,
    ),

]
