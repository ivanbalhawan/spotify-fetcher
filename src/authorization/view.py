import os
import uuid

import requests
import spotipy
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from requests.models import HTTPError
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth

# Reference code https://github.com/perelin/spotipy_oauth_demo/blob/master/spotipy_oauth_demo.py


router = APIRouter()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
PORT_NUMBER = int(os.getenv("PORT_NUMBER", 56626))
URL_ADDRESS = os.getenv("URL_ADDRESS", "http://localhost")
CALLBACK_ENDPOINT = os.getenv("CALLBACK_ENDPOINT", "/callback")
SPOTIPY_REDIRECT_URI = f"{URL_ADDRESS}:{PORT_NUMBER}/callback"

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")
SPOTIPY_SCOPE = os.getenv("SPOTIPY_SCOPE", "user-library-read")
SPOTIPY_CACHE = os.getenv("SPOTIPY_CACHE", ".spotipyoauthcache")

SPOTIPY_STATE: int = uuid.getnode()

sp_oauth = oauth2.SpotifyOAuth(
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI,
    scope=SPOTIPY_SCOPE,
    cache_path=SPOTIPY_CACHE,
    state=SPOTIPY_STATE,
)


async def get_cached_access_token(sp_oauth):
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        return token_info["access_token"]

    return None


@router.get("/login")
async def request_user_authorization():
    """Request user authorization to Spotify API"""
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("You are already authenticated")
        return

    auth_url = sp_oauth.get_authorize_url()
    return f"Open this URL in your browser to login to spotify: {auth_url}"


@router.get("/callback")
async def callback(
    state: str,
    code: str,
    error: str | None = None,
):
    """Callback function"""
    print(f"state: {state}\ncode: {code}\nerror: {error}")

    url = f"/callback?state={state}&code={code}"
    code = sp_oauth.parse_response_code(url)
    if code == url:
        # TODO: Handle wrong scenario
        print("Unable to authenticate. Are you sure you entered the right URL?")
        return

    # We don't care about the access token at this stage
    _ = sp_oauth.get_access_token(code)
    print("Your access token is stored at: .spotipyoauthcache")


@router.get("/saved_tracks")
async def saved_tracks():
    sp_oauth = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        f"{URL_ADDRESS}:{PORT_NUMBER}/saved_tracks",
        scope=SPOTIPY_SCOPE,
        cache_path=SPOTIPY_CACHE,
        state=SPOTIPY_STATE,
    )
    access_token = await get_cached_access_token(sp_oauth)
    if not access_token:
        return RedirectResponse(f"{URL_ADDRESS}:{PORT_NUMBER}/login")

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
        results.extend(result)
        i += 1

    for idx, item in enumerate(results["items"]):
        track = item["track"]
        print(idx, track["artists"][0]["name"], " – ", track["name"])
    return results
