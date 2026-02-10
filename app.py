"""
Flask application for managing users and their movies.

The app supports:
- Listing users
- Creating users
- Viewing a user's movie list
- Adding movies (optionally with OMDb)
- Updating and deleting movies
"""

import os

import requests
from flask import Flask, redirect, render_template, request, url_for

from data_manager import DataManager
from models import Movie, User, db

app = Flask(__name__)

# Database config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'data/movies.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init SQLAlchemy
db.init_app(app)

# Create tables (only if they don't exist)
with app.app_context():
    db.create_all()

# Data access layer
dm = DataManager()


def fetch_movie_from_omdb(title: str) -> dict | None:
    """
    Fetch a movie from OMDb.

    Args:
        title: Movie title to search in OMDb.

    Returns:
        OMDb JSON dict if found and API key is configured; otherwise None.
    """
    api_key = os.environ.get("OMDB_API_KEY", "").strip()
    if not api_key:
        return None

    response = requests.get(
        "https://www.omdbapi.com/",
        params={"apikey": api_key, "t": title},
        timeout=10,
    )
    data = response.json()

    if data.get("Response") != "True":
        return None

    return data


@app.get("/")
def index():
    """
    Render the homepage with the list of users.

    Returns:
        Rendered HTML template.
    """
    users = dm.get_users()
    return render_template("index.html", users=users)


@app.post("/users/<int:user_id>/movies")
def add_movie(user_id: int):
    """
    Add a movie to a specific user.

    If OMDb is available and the movie is found, add
    director/year/poster. Otherwise, a minimal movie entry is created.

    Args:
        user_id: ID of the user to add the movie to.

    Returns:
        Redirect to the user's movies page.
    """
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("user_movies", user_id=user_id))

    data = fetch_movie_from_omdb(title)

    # If OMDb fails (missing key or not found), still add the title
    movie = Movie(
        name=data.get("Title", title) if data else title,
        director=(data.get("Director") if data else None),
        year=(
            int(data["Year"][:4])
            if data and data.get("Year") and data["Year"][:4].isdigit()
            else None
        ),
        poster_url=(data.get("Poster") if data else None),
        user_id=user_id,
    )

    dm.add_movie(movie)
    return redirect(url_for("user_movies", user_id=user_id))


@app.post("/movies/<int:movie_id>/delete")
def delete_movie(movie_id: int):
    """
    Delete a movie by its ID and redirect back to the user's movie page.

    Note:
        This route expects a hidden form field "user_id" to be submitted
        so the redirect can go back to the correct user page.

    Args:
        movie_id: ID of the movie to delete.

    Returns:
        Redirect to the user's movies page.
    """
    dm.delete_movie(movie_id)
    user_id = request.form.get("user_id", type=int)
    return redirect(url_for("user_movies", user_id=user_id))


@app.post("/users/<int:user_id>/movies/<int:movie_id>/delete")
def delete_movie_codio(user_id: int, movie_id: int):
    """
    Delete route that includes user_id in the URL.

    Args:
        user_id: ID of the user owning the movie.
        movie_id: ID of the movie to delete.

    Returns:
        Redirect to the user's movies page.
    """
    dm.delete_movie(movie_id)
    return redirect(url_for("user_movies", user_id=user_id))


@app.post("/users")
def create_user():
    """
    Create a new user using the submitted form field "name".

    Returns:
        Redirect to the homepage.
    """
    name = request.form.get("name", "").strip()
    if name:
        dm.create_user(name)
    return redirect(url_for("index"))


@app.get("/users/<int:user_id>")
def user_movies(user_id: int):
    """
    Render the movies page for a specific user.

    Args:
        user_id: ID of the user whose movies should be displayed.

    Returns:
        Rendered HTML template.
    """
    users = dm.get_users()
    user = User.query.get(user_id)
    movies = dm.get_movies(user_id)

    return render_template(
        "movies.html",
        users=users,
        user=user,
        user_id=user_id,
        movies=movies,
    )


@app.get("/users/<int:user_id>/movies")
def user_movies_alias(user_id: int):
    """
    Alias route for the user's movies page.

    Args:
        user_id: ID of the user.

    Returns:
        Rendered HTML template.
    """
    return user_movies(user_id)


@app.get("/movies/<int:movie_id>/update")
def update_movie_form(movie_id: int):
    """
    Render the update form for a movie.

    Args:
        movie_id: ID of the movie to update

    Returns:
        Rendered HTML template or redirect if movie does not exist.
    """
    movie = Movie.query.get(movie_id)
    if not movie:
        return redirect(url_for("index"))

    return render_template("update_movie.html", movie=movie)


@app.post("/movies/<int:movie_id>/update")
def update_movie(movie_id: int):
    """
    Update a movie by its ID using a submitted "title" field.

    The title is optionally added via OMDb.

    Args:
        movie_id: ID of the movie to update.

    Returns:
        Redirect to the user's movies page.
    """
    movie = Movie.query.get(movie_id)
    if not movie:
        return redirect(url_for("index"))

    user_id = movie.user_id

    new_title = request.form.get("title", "").strip()
    if not new_title:
        return redirect(url_for("user_movies", user_id=user_id))

    data = fetch_movie_from_omdb(new_title)

    payload = {"name": new_title}
    if data:
        payload = {
            "name": data.get("Title", new_title),
            "director": data.get("Director"),
            "year": (
                int(data["Year"][:4])
                if data.get("Year") and data["Year"][:4].isdigit()
                else None
            ),
            "poster_url": data.get("Poster"),
        }

    dm.update_movie(movie_id, payload)
    return redirect(url_for("user_movies", user_id=user_id))


@app.post("/users/<int:user_id>/movies/<int:movie_id>/update")
def update_movie_codio(user_id: int, movie_id: int):
    """
    Args:
        user_id: ID of the user.
        movie_id: ID of the movie to update.

    Returns:
        Redirect to the user's movies page.
    """
    new_title = request.form.get("title", "").strip()
    if not new_title:
        return redirect(url_for("user_movies", user_id=user_id))

    data = fetch_movie_from_omdb(new_title)

    payload = {"name": new_title}
    if data:
        payload = {
            "name": data.get("Title", new_title),
            "director": data.get("Director"),
            "year": (
                int(data["Year"][:4])
                if data.get("Year") and data["Year"][:4].isdigit()
                else None
            ),
            "poster_url": data.get("Poster"),
        }

    dm.update_movie(movie_id, payload)
    return redirect(url_for("user_movies", user_id=user_id))


@app.get("/users")
def list_users():
    """
    List all users as plain text.

    Returns:
        HTML string with user IDs and names.
    """
    users = dm.get_users()
    return "<br>".join([f"{u.id}: {u.name}" for u in users])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    