"""Reference code https://github.com/perelin/spotipy_oauth_demo/blob/master/spotipy_oauth_demo.py."""
from fastapi import APIRouter

from .controller import sp_oauth

router = APIRouter()


@router.get("/login")
async def request_user_authorization():
    """Request user authorization to Spotify API."""
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("You are already authenticated")
        return None

    auth_url = sp_oauth.get_authorize_url()
    return f"Open this URL in your browser to login to spotify: {auth_url}"


@router.get("/callback")
async def callback(
    state: str,
    code: str,
    error: str | None = None,
):
    """Callback function."""
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
