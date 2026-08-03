import services
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from functools import wraps

courses_bp = Blueprint("courses", __name__)

ROLE_LABELS = {
    "student": "Estudiante",
    "instructor": "Docente",
    "admin": "Administrador",
}


def build_schedule(form):
    """Build a readable schedule with an independent range for each weekday."""
    day_1, day_2 = form.get("day_1", ""), form.get("day_2", "")
    start_1, end_1 = form.get("start_time_1", ""), form.get("end_time_1", "")
    start_2, end_2 = form.get("start_time_2", ""), form.get("end_time_2", "")
    if not all((day_1, day_2, start_1, end_1, start_2, end_2)):
        return None, "Selecciona dos días y sus rangos de hora."
    if day_1 not in ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes") or day_2 not in ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes"):
        return None, "Los días del horario deben estar entre lunes y viernes."
    if day_1 == day_2:
        return None, "Los dos días del horario deben ser distintos."
    for start, end in ((start_1, end_1), (start_2, end_2)):
        if not ("08:00" <= start < end <= "21:00"):
            return None, "Cada horario debe estar entre las 08:00 y las 21:00, con fin posterior al inicio."
    return f"{day_1} · {start_1}–{end_1} | {day_2} · {start_2}–{end_2}", None


def schedule_form_values(course=None):
    values = {"day_1": "Lunes", "start_time_1": "08:00", "end_time_1": "10:00", "day_2": "Miércoles", "start_time_2": "08:00", "end_time_2": "10:00"}
    schedule = (course or {}).get("schedule", "")
    try:
        first, second = schedule.split(" | ")
        values["day_1"], first_hours = first.split(" · ")
        values["day_2"], second_hours = second.split(" · ")
        values["start_time_1"], values["end_time_1"] = first_hours.split("–")
        values["start_time_2"], values["end_time_2"] = second_hours.split("–")
    except ValueError:
        try:
            days, hours = schedule.split(" · ")
            values["day_1"], values["day_2"] = days.split(" y ")
            values["start_time_1"], values["end_time_1"] = hours.split("–")
            values["start_time_2"], values["end_time_2"] = values["start_time_1"], values["end_time_1"]
        except ValueError:
            pass
    return values


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "token" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def instructor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") not in ("instructor", "admin"):
            flash("Acceso denegado.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper


def course_owner_or_admin_required(f):
    @wraps(f)
    def wrapper(course_id, *args, **kwargs):
        status, course = services.get_course(session["token"], course_id)
        if status != 200:
            flash("Curso no encontrado.", "danger")
            return redirect(url_for("courses.my_courses"))
        if session.get("role") != "admin" and course.get("instructor_id") != session.get("user_id"):
            flash("Acceso denegado.", "danger")
            return redirect(url_for("index"))
        return f(course_id, *args, **kwargs)

    return wrapper


@courses_bp.route("/courses")
@login_required
def list_courses():
    status, data = services.list_courses(session["token"])
    if status != 200:
        flash("Error al cargar cursos.", "danger")
        data = []
    enrolled_counts = {c["id"]: services.count_enrolled_for(session["token"], c["id"]) for c in data}
    return render_template("courses/list.html", courses=data, enrolled_counts=enrolled_counts)


@courses_bp.route("/courses/mine")
@login_required
@instructor_required
def my_courses():
    status, data = services.my_courses(session["token"])
    if status != 200:
        flash("Error al cargar tus cursos.", "danger")
        data = []
    enrolled_counts = {c["id"]: services.count_enrolled_for(session["token"], c["id"]) for c in data}
    return render_template("courses/mine.html", courses=data, enrolled_counts=enrolled_counts)


@courses_bp.route("/courses/<int:course_id>")
@login_required
def detail(course_id):
    token = session["token"]
    status, course = services.get_course(token, course_id)
    if status != 200:
        flash("Curso no encontrado.", "danger")
        return redirect(url_for("courses.list_courses"))

    enrolled_count = services.count_enrolled_for(token, course_id)

    students = None
    if session.get("role") == "admin" or (
        session.get("role") == "instructor" and course.get("instructor_id") == session.get("user_id")
    ):
        raw = services.enrollments_for_course(token, course_id)
        students = []
        for e in raw:
            _, user = services.get_user(token, e["user_id"])
            if user and "full_name" in user:
                students.append(user)

    return render_template(
        "courses/detail.html",
        course=course,
        enrolled_count=enrolled_count,
        students=students,
    )


@courses_bp.route("/courses/new", methods=["GET", "POST"])
@login_required
@instructor_required
def new_course():
    if request.method == "POST":
        schedule, error = build_schedule(request.form)
        if error:
            flash(error, "danger")
            return render_template("courses/form.html", course=None, schedule=request.form)
        status, data = services.create_course(
            session["token"],
            request.form["title"],
            request.form.get("description", ""),
            request.form["capacity"],
            request.form.get("classroom", "").strip(),
            schedule,
        )
        if status == 201:
            flash("Curso creado.", "success")
            return redirect(url_for("courses.list_courses"))
        flash(data.get("detail", "Error al crear curso."), "danger")

    return render_template("courses/form.html", course=None, schedule=schedule_form_values())


@courses_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
@instructor_required
@course_owner_or_admin_required
def edit_course(course_id):
    token = session["token"]

    if request.method == "POST":
        schedule, error = build_schedule(request.form)
        if error:
            flash(error, "danger")
            return render_template("courses/form.html", course={"title": request.form.get("title", ""), "description": request.form.get("description", ""), "capacity": request.form.get("capacity", 30), "classroom": request.form.get("classroom", "")}, schedule=request.form)
        status, data = services.update_course(
            token,
            course_id,
            request.form["title"],
            request.form.get("description", ""),
            request.form["capacity"],
            request.form.get("classroom", "").strip(),
            schedule,
        )
        if status == 200:
            flash("Curso actualizado.", "success")
            return redirect(url_for("courses.detail", course_id=course_id))
        flash(data.get("detail", "Error al actualizar."), "danger")

    status, course = services.get_course(token, course_id)
    if status != 200:
        flash("Curso no encontrado.", "danger")
        return redirect(url_for("courses.my_courses"))

    return render_template("courses/form.html", course=course, schedule=schedule_form_values(course))


@courses_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
@instructor_required
@course_owner_or_admin_required
def deactivate_course(course_id):
    status = services.deactivate_course(session["token"], course_id)
    if status == 204:
        flash("Curso desactivado.", "info")
    else:
        flash("Error al desactivar el curso.", "danger")
    return redirect(url_for("courses.list_courses"))
