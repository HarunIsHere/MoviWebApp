"""SQLAlchemy models for users and movies."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Represents an application user who can have multiple movies."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    movies = db.relationship(
        "Movie",
        backref="user",
        cascade="all, delete-orphan",
    )


class Movie(db.Model):
    """Represents a movie entry owned by a user."""

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(200), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    