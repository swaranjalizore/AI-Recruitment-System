from flask import Blueprint, render_template, session, redirect, url_for, request, current_app, flash
from database.db import get_db_connection
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

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

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not full_name or not email or not phone:
        flash("Required candidate fields are missing.", "danger")
        return redirect(url_for("candidate.register"))

    if not password or not confirm_password:
            flash("Password fields are required.", "danger")
            return redirect(url_for("candidate.register"))

    if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("candidate.register"))

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500
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
        flash("Email already registered!", "danger")
        return redirect(url_for("candidate.register"))

    query = """
    INSERT INTO candidate
    (full_name, email, password, phone)
    VALUES (%s, %s, %s, %s)
    """

    password_hash = generate_password_hash(password)
    print("Before INSERT")

    cursor.execute(query, (full_name, email, password_hash, phone))

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

    if session.get("role") != "candidate":
        return "Access Denied!"

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    # ================= UPDATE PROFILE =================
    if request.method == "POST":

        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        education = request.form.get("education")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        location = request.form.get("location")

        if not full_name:
            connection.close()
            flash("Full name is required.", "danger")
            return redirect(url_for("candidate.profile"))

        resume = request.files.get("resume")

        resume_filename = None

        if resume and resume.filename != "":

            if not resume.filename.lower().endswith(".pdf"):
                connection.close()
                flash("Only PDF resumes are allowed.", "danger")
                return redirect(url_for("candidate.profile"))

            # Check whether the uploaded file is actually a PDF
            resume.seek(0)
            file_header = resume.read(4)
            resume.seek(0)

            if file_header != b"%PDF":
                connection.close()
                flash("Invalid PDF file.", "danger")
                return redirect(url_for("candidate.profile"))

            original_filename = secure_filename(resume.filename)

            name, extension = os.path.splitext(original_filename)

            resume_filename = f"{session['user_id']}_{name}{extension}"

            upload_folder = os.path.join(
                current_app.root_path,
                "uploads",
                "resumes"
            )

            os.makedirs(upload_folder, exist_ok=True)

            resume.save(
                os.path.join(upload_folder, resume_filename)
            )

        if resume_filename:
            query = """
            UPDATE candidate
            SET
                full_name = %s,
                phone = %s,
                education = %s,
                skills = %s,
                experience = %s,
                location = %s,
                resume_file = %s
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
                    resume_filename,
                    session["user_id"]
                )
            )

        else:
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

        flash("Profile updated successfully.", "success")
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

@candidate.route("/candidate/jobs")
def browse_jobs():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    # Check if logged-in user is a candidate
    if session.get("role") != "candidate":
        return "Access Denied!"

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        job_id,
        job_title,
        description,
        required_skills,
        experience_required,
        salary,
        location,
        employment_type,
        openings,
        posted_date
    FROM Job
    WHERE status = 'Open'
    ORDER BY posted_date DESC
    """

    cursor.execute(query)

    jobs = cursor.fetchall()

    connection.close()

    return render_template(
        "candidate/jobs.html",
        jobs=jobs
    )

@candidate.route("/candidate/job/<int:job_id>")
def job_details(job_id):

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    # Check if logged-in user is a candidate
    if session.get("role") != "candidate":
        return "Access Denied!"

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        job_id,
        job_title,
        description,
        required_skills,
        experience_required,
        salary,
        location,
        employment_type,
        openings,
        posted_date
    FROM Job
    WHERE job_id = %s
    AND status = 'Open'
    """

    cursor.execute(query, (job_id,))

    job = cursor.fetchone()

    connection.close()

    # If job does not exist or is not open
    if not job:
        flash("Job not found or no longer available.", "warning")
        return redirect(url_for("candidate.browse_jobs"))

    return render_template(
        "candidate/job_details.html",
        job=job
    )

@candidate.route("/candidate/job/<int:job_id>/apply", methods=["POST"])
def apply_job(job_id):

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    # Check if logged-in user is a candidate
    if session.get("role") != "candidate":
        return "Access Denied!"

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500
    cursor = connection.cursor(dictionary=True)

    # Check whether the job exists and is still open
    query = """
    SELECT job_id
    FROM Job
    WHERE job_id = %s
    AND status = 'Open'
    """

    cursor.execute(query, (job_id,))

    job = cursor.fetchone()

    if not job:
        connection.close()
        flash("Job not found or no longer available.", "warning")
        return redirect(url_for("candidate.browse_jobs"))

    # Check whether candidate has already applied
    query = """
    SELECT application_id
    FROM application
    WHERE candidate_id = %s
    AND job_id = %s
    """

    cursor.execute(
        query,
        (
            session["user_id"],
            job_id
        )
    )

    existing_application = cursor.fetchone()

    if existing_application:
        connection.close()
        flash("You have already applied for this job.", "warning")
        return redirect(
            url_for(
                "candidate.job_details",
                job_id=job_id
            )
        )

    # Create new application
    query = """
    INSERT INTO application
    (
        candidate_id,
        job_id,
        status
    )
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (
            session["user_id"],
            job_id,
            "Pending"
        )
    )

    connection.commit()
    connection.close()

    flash("Job application submitted successfully.", "success")

    return redirect(
        url_for(
            "candidate.job_details",
            job_id=job_id
        )
    )

@candidate.route("/candidate/applied-jobs")
def applied_jobs():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    # Check if logged-in user is a candidate
    if session.get("role") != "candidate":
        return "Access Denied!"

    connection = get_db_connection()
    if connection is None:
        return "Database connection failed.", 500
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        a.application_id,
        a.application_date,
        a.status,
        a.match_score,

        j.job_id,
        j.job_title,
        j.location,
        j.employment_type,
        j.experience_required,
        j.salary,

        r.company_name

    FROM application a

    INNER JOIN Job j
        ON a.job_id = j.job_id

    INNER JOIN Recruiter r
        ON j.recruiter_id = r.recruiter_id

    WHERE a.candidate_id = %s

    ORDER BY a.application_date DESC
    """

    cursor.execute(
        query,
        (session["user_id"],)
    )

    applications = cursor.fetchall()

    connection.close()

    return render_template(
        "candidate/applied_jobs.html",
        applications=applications
    )