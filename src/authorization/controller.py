from spotipy import oauth2

from src.config import auth_settings
from src.config import backend_settings

sp_oauth = oauth2.SpotifyOAuth(
    auth_settings.spotipy_client_id,
    auth_settings.spotipy_client_secret,
    f"{backend_settings.server_address}:{backend_settings.port_number}/tracks/saved",
    scope=auth_settings.spotipy_scope,
    cache_path=auth_settings.spotipy_cache,
    state=auth_settings.spotipy_state,
)


async def get_cached_access_token(sp_oauth):
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        return token_info["access_token"]

    return None
