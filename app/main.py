from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI

from app.database import create_db_and_tables
from app.oauth2 import oauth2_scheme
from app.oauth2 import router as oauth2_router
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app):
    print("lifespan on-startup")
    create_db_and_tables()
    yield
    print("lifespan on-shutdown")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root(token: Annotated[str, Depends(oauth2_scheme)]):
    print(token)
    return {"Hello": "World"}


app.include_router(oauth2_router)
app.include_router(users_router)
