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


def _build_report(token, courses):
    reports = []
    total_students = 0
    total_occupancy = 0

    for course in courses:
        enrolled = services.count_enrolled_for(token, course["id"])
        capacity = course.get("capacity", 0)
        occupancy = round((enrolled / capacity) * 100) if capacity else 0

        if occupancy == 100:
            status = "Completo"
        elif occupancy >= 70:
            status = "Casi lleno"
        else:
            status = "Disponible"

        total_students += enrolled
        total_occupancy += occupancy
        reports.append(
            {
                "title": course.get("title", "Sin título"),
                "capacity": capacity,
                "enrolled": enrolled,
                "occupancy": occupancy,
                "status": status,
            }
        )

    summary = {
        "courses": len(courses),
        "students": total_students,
        "occupancy": round(total_occupancy / len(courses)) if courses else 0,
    }
    return summary, reports


@reports_bp.route("/")
@login_required
@instructor_required
def index():
    status, courses = services.my_courses(session["token"])
    if status != 200:
        flash("Error al cargar los datos para los reportes.", "danger")
        courses = []

    summary, reports = _build_report(session["token"], courses)
    return render_template("reports/index.html", summary=summary, reports=reports)
