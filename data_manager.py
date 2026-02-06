from models import db, User, Movie


class DataManager:
    def create_user(self, name: str) -> User:
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self) -> list[User]:
        return User.query.order_by(User.name.asc()).all()

    def get_movies(self, user_id: int) -> list[Movie]:
        return Movie.query.filter_by(user_id=user_id).order_by(Movie.name.asc()).all()

    def add_movie(self, movie: Movie) -> Movie:
        # Expecting a fully-populated Movie object (including user_id) from app.py
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id: int, updated_fields: dict) -> Movie | None:
        movie = Movie.query.get(movie_id)
        if not movie:
            return None

        # Update only fields that are provided
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
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        db.session.delete(movie)
        db.session.commit()
        return True