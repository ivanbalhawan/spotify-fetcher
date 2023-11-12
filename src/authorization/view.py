import os
import uuid

import requests
import spotipy
from fastapi import APIRouter
from requests.models import HTTPError
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth

# Reference code https://github.com/perelin/spotipy_oauth_demo/blob/master/spotipy_oauth_demo.py


router = APIRouter()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
PORT_NUMBER = int(os.getenv("PORT_NUMBER", 56626))
SPOTIPY_REDIRECT_URI = f"http://localhost:{PORT_NUMBER}/callback"

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


async def get_access_token():
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        return token_info["access_token"]

    return None


@router.get("/login")
async def request_user_authorization():
    """Request user authorization to Spotify API"""
    access_token = await get_access_token()

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)

        results = sp.current_user_saved_tracks()
        for idx, item in enumerate(results["items"]):
            track = item["track"]
            print(idx, track["artists"][0]["name"], " – ", track["name"])
        return results

    auth_url = getSPOauthURI()
    return auth_url


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


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
    if code != url:
        print(
            "Found Spotify auth code in Request URL! Trying to get valid access token."
        )
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info["access_token"]

    print(f"Access token: {access_token}")
    sp = spotipy.Spotify(access_token)

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results["items"]):
        track = item["track"]
        print(idx, track["artists"][0]["name"], " – ", track["name"])
