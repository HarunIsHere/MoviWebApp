"""Data access layer for User and Movie database operations."""

from models import Movie, User, db


class DataManager:
    """Covers database operations for users and movies."""

    def create_user(self, name: str) -> User:
        """
        Create and persist a new user.

        Args:
            name: The users name.

        Returns:
            The newly created User instance.
        """
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self) -> list[User]:
        """
        Retrieve all users ordered by name (ascending).

        Returns:
            A list of User objects.
        """
        return User.query.order_by(User.name.asc()).all()

    def get_movies(self, user_id: int) -> list[Movie]:
        """
        Retrieve all movies for a given user, ascending movie name.

        Args:
            user_id: Owning user's ID.

        Returns:
            A list of Movie objects for the user.
        """
        return (
            Movie.query.filter_by(user_id=user_id)
            .order_by(Movie.name.asc())
            .all()
        )

    def add_movie(self, movie: Movie) -> Movie:
        """
        Persist a Movie object.

        Args:
            movie: The Movie instance to store.

        Returns:
            The stored Movie instance.
        """
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id: int, updated_fields: dict) -> Movie | None:
        """
        Update specific fields of a movie.

        Args:
            movie_id: ID of the movie to update.
            updated_fields: Dict of fields to update (e.g. name, director, year, poster_url).

        Returns:
            The updated Movie if found, otherwise None.
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            return None

        if "name" in updated_fields:
            movie.name = updated_fields["name"]
        if "director" in updated_fields:
            movie.director = updated_fields["director"]
        if "year" in updated_fields:
            movie.year = updated_fields["year"]
        if "poster_url" in updated_fields:
            movie.poster_url = updated_fields["poster_url"]

        db.session.commit()
        return movie

    def delete_movie(self, movie_id: int) -> bool:
        """
        Delete a movie by its ID.

        Args:
            movie_id: ID of the movie.

        Returns:
            True if deleted; False if not found.
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        db.session.delete(movie)
        db.session.commit()
        return True
        