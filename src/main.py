import fastapi
from fastapi import FastAPI

from src.authorization.view import router as authorization_router

app = FastAPI()

app.include_router(authorization_router)
