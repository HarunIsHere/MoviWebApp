import os
import requests
from flask import Flask, render_template, request, redirect, url_for

from models import db, User, Movie
from data_manager import DataManager

app = Flask(__name__)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///moviwebapp.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init SQLAlchemy
db.init_app(app)

# Create tables (only if they don't exist yet)
with app.app_context():
    db.create_all()

# Data access layer
dm = DataManager()


def fetch_movie_from_omdb(title: str) -> dict | None:
    api_key = os.environ.get("OMDB_API_KEY", "").strip()
    if not api_key:
        return None

    r = requests.get(
        "https://www.omdbapi.com/",
        params={"apikey": api_key, "t": title},
        timeout=10,
    )
    data = r.json()
    if data.get("Response") != "True":
        return None
    return data


@app.get("/")
def index():
    users = dm.get_users()
    return render_template("index.html", users=users)


@app.post("/users/<int:user_id>/movies")
def add_movie(user_id):
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("user_movies", user_id=user_id))

    data = fetch_movie_from_omdb(title)

    # If OMDb fails (missing key or not found), still add minimal movie with just the title
    movie = Movie(
        name=data.get("Title", title) if data else title,
        director=(data.get("Director") if data else None),
        year=(int(data["Year"][:4]) if data and data.get("Year") and data["Year"][:4].isdigit() else None),
        poster_url=(data.get("Poster") if data else None),
        user_id=user_id,
    )

    dm.add_movie(movie)
    return redirect(url_for("user_movies", user_id=user_id))


@app.post("/movies/<int:movie_id>/delete")
def delete_movie(movie_id):
    dm.delete_movie(movie_id)
    # we need to redirect back to the user's page; get user_id from hidden form field
    user_id = request.form.get("user_id", type=int)
    return redirect(url_for("user_movies", user_id=user_id))


@app.post("/users")
def create_user():
    name = request.form.get("name", "").strip()
    if name:
        dm.create_user(name)
    return redirect(url_for("index"))


@app.get("/users/<int:user_id>")
def user_movies(user_id):
    users = dm.get_users()
    user = User.query.get(user_id)
    movies = dm.get_movies(user_id)
    return render_template(
        "user_movies.html",
        users=users,
        user=user,
        user_id=user_id,
        movies=movies
    )


@app.get("/movies/<int:movie_id>/update")
def update_movie_form(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return redirect(url_for("index"))

    return render_template("update_movie.html", movie=movie)


@app.post("/movies/<int:movie_id>/update")
def update_movie(movie_id):
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


if __name__ == "__main__":
    app.run(debug=True)