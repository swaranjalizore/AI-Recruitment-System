from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_db_connection

auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    return render_template("auth/login.html")


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

            session["user_id"] = user["candidate_id"]
            session["name"] = user["full_name"]
            session["role"] = "candidate"

            return redirect(url_for("candidate.dashboard"))
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

            session["user_id"] = user["recruiter_id"]
            session["name"] = user["hr_name"]
            session["role"] = "recruiter"

            return redirect(url_for("recruiter.dashboard"))

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

            session["user_id"] = user["admin_id"]
            session["name"] = user["full_name"]
            session["role"] = "admin"

            return redirect(url_for("admin.dashboard"))

        else:
            return "Invalid Admin Email or Password"
    

    return f"""
    Role: {role}<br>
    Email: {email}<br>
    Password: {password}
    """

@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.home"))