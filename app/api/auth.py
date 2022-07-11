from fastapi import Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict

from app import database, models, utils, oauth2


def login(
        user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(database.get_db)
) -> Dict:
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')

    access_token = oauth2.create_access_token(
        data={"user_id": str(user.id), "scopes": user.scopes})
    return {"access_token": access_token, "token_type": "bearer"}
