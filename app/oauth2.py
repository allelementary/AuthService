import uuid
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWSError, JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import config, database, models, schemas

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={"admin": "ultimate access"},
)

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        idx: str = payload.get("user_id")
        if not idx:
            raise credentials_exception
        token_data = schemas.TokenData(id=idx)
    except JWSError:
        raise credentials_exception
    return token_data


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_session),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = schemas.TokenData(scopes=token_scopes, id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = _get_user(db, idx=token_data.id)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


def _get_user(db, idx: uuid):
    user = db.query(models.User).filter(models.User.id == idx).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist",
        )
    return user

