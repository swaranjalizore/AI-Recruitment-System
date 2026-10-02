from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db_connection
from werkzeug.security import check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    return render_template("home.html")

@auth.route("/login")
def login_page():
    return render_template("auth/login.html")

@auth.route("/login", methods=["POST"])
def login():

    session.clear()
    
    role = request.form["role"]
    email = request.form["email"]
    password = request.form["password"]

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500
    cursor = connection.cursor(dictionary=True)

    if role == "candidate":

        query = """
        SELECT *
        FROM candidate
        WHERE email = %s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["candidate_id"]
            session["name"] = user["full_name"]
            session["role"] = "candidate"

            print("Session after login:", dict(session))
            connection.close()

            return redirect(url_for("candidate.dashboard"))
        else:
            connection.close()
            flash("Invalid Candidate Email or Password.", "danger")
            return redirect(url_for("auth.login_page"))
        
    elif role == "recruiter":

        query = """
        SELECT *
        FROM recruiter
        WHERE email = %s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["recruiter_id"]
            session["name"] = user["hr_name"]
            session["role"] = "recruiter"
            connection.close()

            return redirect(url_for("recruiter.dashboard"))

        else:
            connection.close()
            flash("Invalid Recruiter Email or Password.", "danger")
            return redirect(url_for("auth.login_page"))
        
    elif role == "admin":

        query = """
        SELECT *
        FROM admin
        WHERE email = %s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["admin_id"]
            session["name"] = user["full_name"]
            session["role"] = "admin"
            connection.close()

            return redirect(url_for("admin.dashboard"))

        else:
            connection.close()
            flash("Invalid Admin Email or Password.", "danger")
            return redirect(url_for("auth.login_page"))
    

    return "Invalid role selected.", 400

@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.home"))