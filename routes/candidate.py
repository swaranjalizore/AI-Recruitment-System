from flask import Blueprint, render_template, session, redirect, url_for

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