from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import EmailStr
from sqlmodel import select

from app.users.models import User, UserCreate, UserResponse
from app.database import SessionDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_email}", response_model=UserResponse)
def read_user(user_email: EmailStr, session: SessionDep):
    user = session.get(User, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, session: SessionDep):
    valid_user = User.model_validate(user)
    existing_user = session.get(User, valid_user.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    session.add(valid_user)
    session.commit()
    session.refresh(valid_user)
    return valid_user


@router.delete("/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_email: EmailStr, session: SessionDep):
    user = session.get(User, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
