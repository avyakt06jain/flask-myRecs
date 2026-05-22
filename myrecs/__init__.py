import os

from flask import Flask, redirect, url_for

from .auth import auth_bp
from .database import close_db, init_db, initialize_database
from .records import cents_to_money
from .records import records_bp
from .security import configure_security_headers


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="../static",
        template_folder="../templates",
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=default_database_path(app.instance_path),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    configure_security_headers(app)
    app.jinja_env.filters["money"] = cents_to_money

    @app.before_request
    def ensure_database():
        initialize_database(seed_demo=False)

    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)

    @app.route("/")
    def index():
        return redirect(url_for("records.dashboard"))

    @app.route("/login")
    def legacy_login():
        return redirect(url_for("auth.login"))

    @app.route("/recs")
    def legacy_records():
        return redirect(url_for("records.dashboard"))

    @app.route("/addingrecs")
    def legacy_new_record():
        return redirect(url_for("records.create"))

    return app


def default_database_path(instance_path):
    configured_database = os.environ.get("DATABASE")
    if configured_database:
        return configured_database
    if os.environ.get("VERCEL"):
        return "/tmp/myrecs.sqlite3"
    return os.path.join(instance_path, "myrecs.sqlite3")
