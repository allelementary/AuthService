# AUTHENTICATION API SERVICE

#### Role-based Authentication API service designed as a part of microservice architecture project

## Usage

- Install python 3.10 and create virtual environment
- Activate environment and install requirements

```bash
# install requirements
pip install -r requirements.txt

# install dev-requirements (for tests)
pip install -r requirements-dev.txt
```

- Create .env file in root directory of the project, fill up database and security credentials

```bash
# example
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=password
DATABASE_NAME=databasename
DATABASE_USERNAME=username
SECRET_KEY=secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=5
```

- Run tests

```commandline
pytest -vv -s -x
```

- Run local server

```commandline
uvicorn app.main:app
```

- Routes available at

```commandline
http://127.0.0.1:8000/docs
```

## Build with

- Python 3.10
- Fastapi
- PostgreSQL
- SQLALchemy
- oAuth2
- Alembic

## Available roles

- Base
- Admin

## Contacts

#### Mikhail Antonov *allelementaryfor@gmail.com*
