from functools import wraps

import services
from flask import Blueprint, flash, redirect, render_template, session, url_for

reports_bp = Blueprint("reports", __name__)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "token" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper


def instructor_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != "instructor":
            flash("Acceso denegado.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapper


@reports_bp.route("/")
@login_required
@instructor_required
def index():
    status, data = services.reports_overview(session["token"])
    if status != 200:
        flash("Error al cargar los datos para los reportes.", "danger")
        data = {"summary": {"courses": 0, "students": 0, "occupancy": 0}, "reports": []}

    return render_template("reports/index.html", summary=data["summary"], reports=data["reports"])
