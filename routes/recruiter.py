from flask import Blueprint, render_template, session, redirect, url_for

recruiter = Blueprint("recruiter", __name__)


@recruiter.route("/recruiter/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    if session.get("role") != "recruiter":
        return "Access Denied!"

    return render_template("recruiter/dashboard.html")