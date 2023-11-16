import os

import spotipy
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.authorization.controller import get_cached_access_token
from src.authorization.controller import sp_oauth
from src.config import backend_settings

router = APIRouter()


@router.get("/saved")
async def saved_tracks():
    access_token = await get_cached_access_token(sp_oauth)
    if not access_token:
        return RedirectResponse(
            f"{backend_settings.server_address}:{backend_settings.port_number}/login"
        )

    print("Access token available! Trying to get user information...")
    sp = spotipy.Spotify(access_token)

    LIMIT: int = int(os.getenv("LIMIT", "50"))
    i: int = 0
    results = []
    while True:
        offset = LIMIT * i
        result = sp.current_user_saved_tracks(limit=LIMIT, offset=offset)
        if result["next"] is None:
            break

        print(result["next"])
        results.extend(result["items"])
        i += 1
        break

    print(f"Found {len(results)} tracks")
    # print(results[0])
    # for idx, item in enumerate(results["items"]):
    #     track = item["track"]
    #     print(idx, track["artists"][0]["name"], " - ", track["name"])

    return results[0]
