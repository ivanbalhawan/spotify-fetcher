# spotify-fetcher

This project fetches your saved tracks from Spotify.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)



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
