import uuid

from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from .. import database
from .. import oauth2


router = APIRouter(
    prefix="/users",
    tags=['CRUD Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_password = utils.hash_pass(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{idx}', response_model=schemas.UserOut)
def get_user(idx: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == idx).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {idx} does not exist")
    return user


@router.delete("/{idx}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        idx: int, db: Session = Depends(database.get_db),
        current_user: int = Depends(oauth2.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == idx).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {idx} does not exist")
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action")
    user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.UserCreate)
def update_user(
        idx: int,
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


# @router.patch("/update-permission/{id}", response_model=schemas.UserPermission)
# def update_user_permission(
#         idx: uuid,
#         updated_user: schemas.UserCreate,
#         db: Session = Depends(database.get_db),
#         current_user: int = Depends(oauth2.get_current_user),
# ):
#     """
#     User roles: 'base', 'trade', 'admin'
#     # todo create types of subscriptions: 'year', 'month', 'free-trial'
#     #  implement payment
#     """
#     user_query = db.query(models.User).filter(models.User.id == idx)
#     user = user_query.first()
#     user_query.patch(updated_user.dict(), synchronize_session=False)
