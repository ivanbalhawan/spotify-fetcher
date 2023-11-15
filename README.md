# spotify-fetcher

This project fetches your saved tracks from Spotify.


## Install dependencies

```bash
pdm install --dev
```


## Start backend

To start

```bash
pdm start
```


## Test login


```bash
http GET http://localhost:56626/login
```


## Test redirection

```bash
rm -f .spotipyoauthcache
http --follow  GET http://localhost:56626/saved_tracks
```

## Test saved tracks
```bash
http --follow  GET http://localhost:56626/saved_tracks
```
