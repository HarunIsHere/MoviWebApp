from flask import Flask, render_template, request, redirect, url_for
from models import db
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


@app.get("/")
def index():
    users = dm.get_users()
    return render_template("index.html", users=users)


@app.post("/users")
def create_user():
    name = request.form.get("name", "").strip()
    if name:
        dm.create_user(name)
    return redirect(url_for("index"))


@app.get("/users/<int:user_id>")
def user_movies(user_id):
    users = dm.get_users()
    movies = dm.get_movies(user_id)
    return render_template("user_movies.html", users=users, user_id=user_id, movies=movies)


if __name__ == "__main__":
    app.run(debug=True)