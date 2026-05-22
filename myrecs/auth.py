from sqlite3 import IntegrityError

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .database import get_db
from .security import csrf_token, load_logged_in_user, validate_csrf


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.before_app_request
def before_request():
    load_logged_in_user()
    validate_csrf()


@auth_bp.app_context_processor
def inject_globals():
    return {"csrf_token": csrf_token}


@auth_bp.route("/register", methods=("GET", "POST"))
def register():
    if g.get("user"):
        return redirect(url_for("records.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        error = validate_registration(name, email, password)

        if error is None:
            try:
                db = get_db()
                cursor = db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password)),
                )
                db.commit()
                session.clear()
                session["user_id"] = cursor.lastrowid
                flash("Account created. Your workspace is ready.", "success")
                return redirect(url_for("records.dashboard"))
            except IntegrityError:
                error = "An account with that email already exists."

        flash(error, "error")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    if g.get("user"):
        return redirect(url_for("records.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("Signed in successfully.", "success")
            return redirect(request.args.get("next") or url_for("records.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("auth.login"))


def validate_registration(name, email, password):
    if len(name) < 2:
        return "Name must be at least 2 characters."
    if "@" not in email or "." not in email:
        return "Enter a valid email address."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    return None
