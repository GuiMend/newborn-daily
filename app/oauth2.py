from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlmodel import select

from app.config import settings
from app.database import SessionDep
from app.users.models import User

SECRET_KEY = settings.hash_secret_key
ALGORITHM = settings.hash_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

LOGIN_URL = "login"

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=LOGIN_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


@router.post(f"/{LOGIN_URL}", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    user = authenticate_user(
        email=form_data.username, password=form_data.password, session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": f"{user.id}"},  # subject must be a string
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def authenticate_user(email: EmailStr, password: str, session: SessionDep):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # "sub" is the JWT subject (unique identifier of the user - ID in this case)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return TokenData(id=user_id)
    except InvalidTokenError:
        raise credentials_exception


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = session.get(User, token_data.id)

    if user is None:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
