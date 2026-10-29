
import os
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "v1").lower()
DATABASE = os.environ.get("DATABASE_PATH", "feedback.db")

VERSION_FEATURES = {
    "v1": 1,
    "v2": 2,
    "v3": 3,
}

if APP_VERSION not in VERSION_FEATURES:
    raise ValueError("APP_VERSION must be v1, v2, or v3")

FEATURE_LEVEL = VERSION_FEATURES[APP_VERSION]


def get_connection():
    db_path = Path(DATABASE)
    if str(db_path.parent) != ".":
        db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


initialize_database()


@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()

        try:
            rating = int(request.form.get("rating", "0"))
        except ValueError:
            rating = 0

        if not name or not message or not 1 <= rating <= 5:
            error = "Enter your name, a message, and a rating from 1 to 5."
        else:
            with get_connection() as connection:
                connection.execute(
                    "INSERT INTO feedback (name, rating, message) "
                    "VALUES (?, ?, ?)",
                    (name, rating, message)
                )

            return redirect(url_for("home", submitted="1"))

    submitted = request.args.get("submitted") == "1"

    return render_template(
        "index.html",
        version=APP_VERSION,
        feature_level=FEATURE_LEVEL,
        error=error,
        submitted=submitted,
    )


@app.route("/feedback")
def view_feedback():
    if FEATURE_LEVEL < 2:
        return "Feedback viewing is available in V2 and V3.", 404

    rating = request.args.get("rating", "").strip()
    query = "SELECT * FROM feedback"
    parameters = []

    if FEATURE_LEVEL >= 3 and rating:
        try:
            rating_value = int(rating)
            if not 1 <= rating_value <= 5:
                raise ValueError
        except ValueError:
            return "Rating must be a number from 1 to 5.", 400

        query += " WHERE rating = ?"
        parameters.append(rating_value)

    query += " ORDER BY id DESC"

    with get_connection() as connection:
        feedback_list = connection.execute(
            query, parameters
        ).fetchall()

    return render_template(
        "feedback.html",
        version=APP_VERSION,
        feature_level=FEATURE_LEVEL,
        feedback_list=feedback_list,
        selected_rating=rating,
    )


@app.route("/health")
def health():
    return {"status": "healthy", "version": APP_VERSION}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
