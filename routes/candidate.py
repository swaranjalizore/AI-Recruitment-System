from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from database.db import get_db_connection
import os
from werkzeug.utils import secure_filename

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

        resume = request.files.get("resume")

        resume_filename = None

        if resume and resume.filename != "":

            if not resume.filename.lower().endswith(".pdf"):
                connection.close()
                return "Only PDF resumes are allowed."

            resume_filename = secure_filename(resume.filename)

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
        return "Job not found or no longer available."

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
        return "Job not found or no longer available."

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
        return "You have already applied for this job."

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