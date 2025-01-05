from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.oauth2 import router as oauth2_router
from app.users.router import router as users_router
from app.babies.router import router as babies_router


@asynccontextmanager
async def lifespan(app):
    print("lifespan on-startup")
    create_db_and_tables()
    yield
    print("lifespan on-shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(oauth2_router)
app.include_router(users_router)
app.include_router(babies_router)
