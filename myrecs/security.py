import secrets
from functools import wraps

from flask import abort, g, redirect, request, session, url_for

from .database import get_db


def configure_security_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_db().execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def load_logged_in_user():
    g.user = current_user()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)

    return wrapped_view


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        sent_token = request.form.get("_csrf_token", "")
        if not sent_token or sent_token != session.get("_csrf_token"):
            abort(400, description="Invalid CSRF token")
