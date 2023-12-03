import uvicorn
from fastapi import FastAPI

from authorization.view import router as authorization_router
from config import backend_settings
from tracks.view import router as tracks_router

app = FastAPI()


app.include_router(authorization_router, prefix="/authorization")
app.include_router(tracks_router, prefix="/tracks")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=backend_settings.port_number, reload=True)
