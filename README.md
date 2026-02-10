# MoviWebApp (Flask + SQLAlchemy)

A small Flask web app to manage **users** and their **favorite movies**. Movies can be enriched with data from **OMDb** (poster, director, year) if an API key is provided.

## Features
- Create users
- View a user's movies
- Add a movie (optionally fetches data from OMDb)
- Update a movie title (optionally re-fetches OMDb data)
- Delete a movie
- SQLite database stored at `data/movies.db`

## Requirements
- Python 3.x
- Dependencies in `requirements.txt`

## Setup

Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate