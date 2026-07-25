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

@candidate.route("/candidate/profile", methods=["GET", "POST"])
def profile():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # ================= UPDATE PROFILE =================
    if request.method == "POST":

        full_name = request.form["full_name"]
        phone = request.form["phone"]
        education = request.form["education"]
        skills = request.form["skills"]
        experience = request.form["experience"]
        location = request.form["location"]

        query = """
        UPDATE candidate
        SET
            full_name = %s,
            phone = %s,
            education = %s,
            skills = %s,
            experience = %s,
            location = %s
        WHERE candidate_id = %s
        """

        cursor.execute(
            query,
            (
                full_name,
                phone,
                education,
                skills,
                experience,
                location,
                session["user_id"]
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("candidate.profile"))

    # ================= SHOW PROFILE =================
    query = """
    SELECT *
    FROM candidate
    WHERE candidate_id = %s
    """

    cursor.execute(query, (session["user_id"],))

    user = cursor.fetchone()

    connection.close()

    return render_template(
        "candidate/profile.html",
        user=user
    )