from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from database.db import get_db_connection
from werkzeug.security import generate_password_hash

recruiter = Blueprint("recruiter", __name__)


@recruiter.route("/recruiter/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    if session.get("role") != "recruiter":
        return "Access Denied!"

    return render_template("recruiter/dashboard.html")

@recruiter.route("/recruiter/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("recruiter/register.html")

    company_name = request.form.get("company_name")
    hr_name = request.form.get("hr_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    company_location = request.form.get("company_location")
    designation = request.form.get("designation")

    if not company_name or not hr_name or not email or not phone:
        flash("Required recruiter fields are missing.", "danger")
        return redirect(url_for("recruiter.register"))

    if not password or not confirm_password:
        flash("Password fields are required.", "danger")
        return redirect(url_for("recruiter.register"))

    if password != confirm_password:
        flash("Passwords do not match!", "danger")
        return redirect(url_for("recruiter.register"))

    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT recruiter_id
    FROM recruiter
    WHERE email = %s
    """

    cursor.execute(query, (email,))
    existing_recruiter = cursor.fetchone()

    if existing_recruiter:
        connection.close()
        flash("Email already registered!", "danger")
        return redirect(url_for("recruiter.register"))
    query = """
    SELECT recruiter_id
    FROM recruiter
    WHERE phone = %s
    """

    cursor.execute(query, (phone,))
    existing_recruiter = cursor.fetchone()

    if existing_recruiter:
        connection.close()
        flash("Phone number already registered!", "danger")
        return redirect(url_for("recruiter.register"))

    password_hash = generate_password_hash(password)

    query = """
    INSERT INTO recruiter
    (
        company_name,
        hr_name,
        email,
        password,
        phone,
        company_location,
        designation
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            company_name,
            hr_name,
            email,
            password_hash,
            phone,
            company_location,
            designation
        )
    )

    connection.commit()
    connection.close()

    return redirect(url_for("auth.login_page"))

@recruiter.route("/recruiter/profile", methods=["GET", "POST"])
def profile():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    # Check if logged-in user is a recruiter
    if session.get("role") != "recruiter":
        return "Access Denied!"

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    # ================= UPDATE PROFILE =================
    if request.method == "POST":

        company_name = request.form.get("company_name")
        hr_name = request.form.get("hr_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        company_location = request.form.get("company_location")
        designation = request.form.get("designation")

        if not company_name or not hr_name or not email or not phone:
            connection.close()
            return "Required recruiter fields are missing."

        # Check whether the email is already used
        query = """
        SELECT recruiter_id
        FROM recruiter
        WHERE email = %s
        AND recruiter_id != %s
        """

        cursor.execute(
            query,
            (
                email,
                session["user_id"]
            )
        )

        existing_recruiter = cursor.fetchone()

        if existing_recruiter:
            connection.close()
            return "Email already registered by another recruiter."

        # Check whether the phone number is already used
        query = """
        SELECT recruiter_id
        FROM recruiter
        WHERE phone = %s
        AND recruiter_id != %s
        """

        cursor.execute(
            query,
            (
                phone,
                session["user_id"]
            )
        )

        existing_recruiter = cursor.fetchone()

        if existing_recruiter:
            connection.close()
            return "Phone number already registered by another recruiter."

        # Update recruiter profile
        query = """
        UPDATE recruiter
        SET
            company_name = %s,
            hr_name = %s,
            email = %s,
            phone = %s,
            company_location = %s,
            designation = %s
        WHERE recruiter_id = %s
        """

        cursor.execute(
            query,
            (
                company_name,
                hr_name,
                email,
                phone,
                company_location,
                designation,
                session["user_id"]
            )
        )

        connection.commit()

        # Update session name if HR name was changed
        session["name"] = hr_name

        connection.close()

        return redirect(url_for("recruiter.profile"))

    # ================= SHOW PROFILE =================

    query = """
    SELECT
        recruiter_id,
        company_name,
        hr_name,
        email,
        phone,
        company_location,
        designation,
        created_at
    FROM recruiter
    WHERE recruiter_id = %s
    """

    cursor.execute(
        query,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    connection.close()

    if not user:
        return "Recruiter profile not found."

    return render_template(
        "recruiter/profile.html",
        user=user
    )