import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user

from app.database import db
from app.modules.courses.routes import courses_bp
from app.modules.enrollments.routes import enrollments_bp
from app.modules.users.routes import users_bp
from app.modules.users.services import get_user_by_id


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-not-for-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://appuser:06nJHZJswgIFq56@mono_postgres:5432/appdb",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "users.login"
    login_manager.login_message = "Inicia sesión para continuar."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    app.register_blueprint(users_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(enrollments_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("courses.list_courses"))
        return redirect(url_for("users.login"))

    return app


app = create_app()
