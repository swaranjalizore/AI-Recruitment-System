from flask import Blueprint, render_template, request, redirect, url_for
from database.db import get_db_connection

auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login():

    role = request.form["role"]
    email = request.form["email"]
    password = request.form["password"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if role == "candidate":

        query = """
        SELECT *
        FROM candidate
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        user = cursor.fetchone()

        if user:
            return f"Welcome {user['full_name']}!"

        else:
            return "Invalid Candidate Email or Password"
        
    elif role == "recruiter":

        query = """
        SELECT *
        FROM recruiter
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        user = cursor.fetchone()

        if user:
            return f"Welcome Recruiter {user['hr_name']}!"

        else:
            return "Invalid Recruiter Email or Password"
        
    elif role == "admin":

        query = """
        SELECT *
        FROM admin
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        user = cursor.fetchone()

        if user:
            return f"Welcome Admin {user['full_name']}!"

        else:
            return "Invalid Admin Email or Password"
    

    return f"""
    Role: {role}<br>
    Email: {email}<br>
    Password: {password}
    """