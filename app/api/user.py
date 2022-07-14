from typing import Dict
from pydantic import UUID4
from fastapi import status, HTTPException, Depends, Response, Security, Path, Query
from sqlalchemy.orm import Session

from app import models, schemas, utils, database, oauth2


def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_session)):
    user_exists = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user.email} already exists"
        )

    hashed_password = utils.hash_pass(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user(idx: UUID4, db: Session = Depends(database.get_session)):
    user = db.query(models.User).filter(models.User.id == idx).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    return user


def delete_user(
        idx: UUID4,
        db: Session = Depends(database.get_session),
        current_user: int = Depends(oauth2.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == idx).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def update_user(
        idx: UUID4,
        updated_user: schemas.UserCreate,
        db: Session = Depends(database.get_session),
        current_user: int = Depends(oauth2.get_current_user)
):
    user_query = db.query(models.User).filter(models.User.id == idx)
    user = user_query.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action")
    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()


def admin_access(user: schemas.UserOut = Security(oauth2.get_current_user, scopes=["admin"])):
    return [{"item_id": "Foo", "owner": user.email}]


def update_user_permission(
        scope: str = Query(...),
        denied_access: bool = Query(...),
        idx: UUID4 = Path(...),
        db: Session = Depends(database.get_session),
        current_user: schemas.UserOut = Security(oauth2.get_current_user, scopes=["admin"]),
) -> Dict:
    """
    User scopes:
    - registered: account created, email does not confirm yet
    - confirmed: email confirmed
    - admin: account has admin permission

    Update user permissions by adding or removing scopes
    :param idx: id of user to update rights
    :param scope: string scope adding to user scopes
                   options: ["admin"]
    :param db: database session
    :param current_user: check current user permissions, should have `admin` scopes
    :param denied_access: False if enable access, True if denied
    :return dict `user_id`: user_id, `scopes`: user_scopes
    """
    current_user_id = current_user.id
    if denied_access:
        user = disable_access(idx, db)
    else:
        user = enable_access(idx, scope, db)
    return {"user_id": user.id, "scopes": [scope]}


def enable_access(
    idx: UUID4,
    scope: str,
    db: Session,
):
    """
    Enable user access by adding scopes
    :param idx: id of user to update rights
    :param scope: string scope adding to user scopes
                   options: ["admin"]
    :param db: database session
    :return: user
    """
    user_query = db.query(models.User).filter(models.User.id == idx)
    user = user_query.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    user_query.update({"scopes": [scope]}, synchronize_session=False)
    db.commit()
    return user


def disable_access(
        idx: UUID4,
        db: Session,
):
    """
    Disable user access by removing scopes
    :param idx: id of user to update rights
    :param db: database session
    :return: user
    """
    user_query = db.query(models.User).filter(models.User.id == idx)
    user = user_query.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    user_query.update({"scopes": []}, synchronize_session=False)
    db.commit()
    return user

# 597f6b38-531d-49b5-b8a9-9f3ce7b901c8
