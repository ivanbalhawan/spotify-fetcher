from fastapi import FastAPI

from src.authorization.view import router as authorization_router
from src.tracks.view import router as tracks_router

app = FastAPI()


app.include_router(authorization_router, prefix="/authorization")
app.include_router(tracks_router, prefix="/tracks")
