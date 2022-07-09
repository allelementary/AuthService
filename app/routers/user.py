from pydantic import UUID4

from fastapi import status, HTTPException, Depends, APIRouter, Response, Security
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from .. import database
from .. import oauth2
from ..oauth2 import get_current_user
from ..schemas import UserOut

router = APIRouter(
    prefix="/users",
    tags=['CRUD Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    user_exists = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user.email} already not exists"
        )

    hashed_password = utils.hash_pass(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{idx}', response_model=schemas.UserOut)
def get_user(idx: UUID4, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == idx).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    return user


@router.delete("/{idx}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        idx: UUID4,
        db: Session = Depends(database.get_db),
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


@router.put("/{id}", response_model=schemas.UserCreate)
def update_user(
        idx: UUID4,
        updated_user: schemas.UserCreate,
        db: Session = Depends(database.get_db),
        current_user: int = Depends(oauth2.get_current_user)
):
    user_query = db.query(models.User).filter(models.User.id == idx)
    user = user_query.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {idx} does not exist"
        )
    if user.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action")
    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()


@router.post("/access", status_code=status.HTTP_201_CREATED)
def access(user: UserOut = Security(get_current_user, scopes=["trade"])):
    breakpoint()
    return [{"item_id": "Foo", "owner": user.email}]


@router.patch("/update-permission/{id}", response_model=schemas.UserPermission)
def update_user_permission(
        idx: UUID4,
        db: Session = Depends(database.get_db),
        current_user: UserOut = Security(get_current_user, scopes=["admin"]),
):
    # todo create types of subscriptions: 'year', 'month', 'free-trial'
    #  implement payment
    """
    User scopes:
    - registered: account created, email does not confirmed yet
    - confirmed: email confirmed
    - trade: account has trade permission
    - admin: account has admin permission
    #  implement payment
    """
    user_query = db.query(models.User).filter(models.User.id == idx)
    user_query.update({"scopes": ["trade"]}, synchronize_session=False)
    user = user_query.first()
    return {"user_id": user.id, "scopes": user.scopes}

# 597f6b38-531d-49b5-b8a9-9f3ce7b901c8
