import os

import pandas as pd
import spotipy
from attrs import frozen
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.authorization.controller import get_cached_access_token
from src.authorization.controller import sp_oauth
from src.config import backend_settings

router = APIRouter()


@frozen
class TrackFeatures:
    track_id: str
    track_name: str
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: float
    time_signature: int

    @classmethod
    def from_series(cls, features_series: pd.Series) -> "TrackFeatures":
        features_dict = features_series.to_dict()
        return cls(**features_dict)

    def __iter__(self):
        for k in self.__slots__:
            if not k.startswith("_"):
                v = self.__getattribute__(k)
                yield k, v


async def saved_tracks_to_df(result):
    tracks_df = pd.DataFrame(
        [
            {"track_id": item["track"]["id"], "track_name": item["track"]["name"]}
            for item in result.get("items", [])
        ]
    )
    return tracks_df


async def request_saved_tracks(sp, iteration: int):
    LIMIT: int = int(os.getenv("LIMIT", "50"))

    offset = LIMIT * iteration
    result = sp.current_user_saved_tracks(limit=LIMIT, offset=offset)

    return result


async def request_track_features(sp, tracks_df):
    track_id_list = tracks_df.track_id.to_list()
    track_features = sp.audio_features(track_id_list)
    track_features_df = pd.DataFrame(track_features)
    track_features_df.rename({"id": "track_id"}, axis=1, inplace=True)
    track_features_df.drop(
        columns=[
            "type",
            "uri",
            "track_href",
            "analysis_url",
        ],
        inplace=True,
    )
    # WARN: this is assuming that the order is always consistent
    track_features_df["track_name"] = tracks_df["track_name"]

    return track_features_df


@router.get("/saved")
async def saved_tracks():
    access_token = await get_cached_access_token(sp_oauth)
    if not access_token:
        return RedirectResponse(
            f"{backend_settings.server_address}:{backend_settings.port_number}/authorization/login"
        )

    print("Access token available! Trying to get user information...")
    sp = spotipy.Spotify(access_token)

    i: int = 0
    features_result = pd.DataFrame()
    while True:
        result = await request_saved_tracks(sp, i)
        i += 1
        print(result["next"])

        if result is None:
            break

        tracks_df = await saved_tracks_to_df(result)
        if tracks_df is not None and not tracks_df.empty:
            track_features_df = await request_track_features(sp, tracks_df)

            if features_result.empty:
                features_result = track_features_df
            else:
                features_result = pd.concat([features_result, track_features_df], ignore_index=True)

    track_features_list = [
        TrackFeatures.from_series(row) for _, row in track_features_df.iterrows()
    ]

    return track_features_list
