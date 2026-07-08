from flask import Flask, render_template
from config import Config
from database.db import get_db_connection

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def home():
    connection = get_db_connection()

    if connection:
        connection.close()
        return render_template("login.html")

    return "❌ Database connection failed!"


if __name__ == "__main__":
    app.run(debug=True)