import os
from attrs import frozen
from attrs import field

import spotipy
import pandas as pd
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.authorization.controller import get_cached_access_token
from src.authorization.controller import sp_oauth
from src.config import backend_settings

router = APIRouter()


@frozen
class TrackFeatures:
    track_id : str
    track_name : str
    danceability : float
    energy : float
    key : int
    loudness : float
    mode : int
    speechiness : float
    acousticness : float
    instrumentalness : float
    liveness : float
    valence : float
    tempo : float
    duration_ms : float
    time_signature : int

    @classmethod
    def from_series(cls, features_series: pd.Series):
        features_dict = features_series.to_dict()
        return cls(**features_dict)

    def __iter__(self):
        for k in self.__slots__:
            if not k.startswith("_"):
                v = self.__getattribute__(k)
                yield k, v


@router.get("/saved")
async def saved_tracks():
    access_token = await get_cached_access_token(sp_oauth)
    if not access_token:
        return RedirectResponse(
            f"{backend_settings.server_address}:{backend_settings.port_number}/authorization/login"
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

    tracks_df = pd.DataFrame([
        {"track_id": item["track"]["id"], "track_name": item["track"]["name"]}
        for item in results
    ])
    track_id_list = tracks_df.track_id.to_list()

    all_features = sp.audio_features(track_id_list)
    audio_features_df = pd.DataFrame(all_features)
    audio_features_df.rename({"id": "track_id"}, axis=1, inplace=True)
    audio_features_df.drop(columns=[
        "type",
        "uri",
        "track_href",
        "analysis_url",
    ], inplace=True)
    # WARN: this is assuming that the order is always consistent
    audio_features_df["track_name"] = tracks_df["track_name"]

    track_features_list = [
        TrackFeatures.from_series(row)
        for _, row in audio_features_df.iterrows()
    ]

    return track_features_list
