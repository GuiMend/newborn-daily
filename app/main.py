from contextlib import asynccontextmanager
from typing import Annotated, Union
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel
from app.database import create_db_and_tables
from app.users.router import router as users_router
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


@asynccontextmanager
async def lifespan(app):
    print("lifespan on-startup")
    create_db_and_tables()
    yield
    print("lifespan on-shutdown")


app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class Token(SQLModel):
    access_token: str
    token_type: str


@app.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # TODO: login
    return {"access_token": form_data}


@app.get("/")
def read_root(token: Annotated[str, Depends(oauth2_scheme)]):
    print(token)
    return {"Hello": "World"}


app.include_router(users_router)
