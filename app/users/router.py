from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.database import SessionDep
from app.oauth2 import CurrentUserDep, get_password_hash
from app.users.models import User, UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: CurrentUserDep):
    return current_user


@router.get("/", response_model=List[UserResponse])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{id}", response_model=UserResponse)
def read_user(id: str, session: SessionDep):
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, session: SessionDep):
    valid_user = User.model_validate(user)
    existing_user = session.exec(
        select(User).where(User.email == valid_user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash the password before storing it in the database
    valid_user.password = get_password_hash(valid_user.password)

    session.add(valid_user)
    session.commit()
    session.refresh(valid_user)
    return valid_user


# TODO: improve patch
@router.patch("/{id}", response_model=UserResponse)
def update_user(id: str, user: UserCreate, session: SessionDep):
    valid_user = User.model_validate(user)
    existing_user = session.get(User, id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_user.email = valid_user.email
    existing_user.first_name = valid_user.first_name
    existing_user.last_name = valid_user.last_name
    existing_user.password = get_password_hash(valid_user.password)

    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: str, session: SessionDep) -> None:
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
