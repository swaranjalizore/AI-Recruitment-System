from flask import Blueprint, render_template, session, redirect, url_for, request
from database.db import get_db_connection

candidate = Blueprint("candidate", __name__)


@candidate.route("/candidate/dashboard")
def dashboard():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    # Check if logged in user is a candidate
    if session.get("role") != "candidate":
        return "Access Denied!"

    return render_template("candidate/dashboard.html")

@candidate.route("/candidate/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("candidate/register.html")

    full_name = request.form["full_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    
    if password != confirm_password:
        return "Passwords do not match!"

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM candidate
    WHERE email = %s
    """

    cursor.execute(query, (email,))

    user = cursor.fetchone()
    if user:
        connection.close()
        return "Email already registered!"

    query = """
    INSERT INTO candidate
    (full_name, email, password, phone)
    VALUES (%s, %s, %s, %s)
    """

    print("Before INSERT")

    cursor.execute(query, (full_name, email, password, phone))

    print("After INSERT")

    connection.commit()

    print("After COMMIT")

    connection.close()

    print("Connection Closed")

    return redirect(url_for("auth.login_page"))