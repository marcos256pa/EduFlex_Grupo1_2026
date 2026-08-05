from datetime import time

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.modules.courses import services
from app.modules.courses.schemas import CourseForm
from app.modules.enrollments.services import list_enrollments_for_course
from app.modules.users.services import get_user_by_id

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

def _build_schedule(form: CourseForm) -> str | None:
    if form.day_1.data == form.day_2.data:
        form.day_2.errors.append("Los dos días del horario deben ser distintos.")
        return None

    ranges = ((form.start_time_1, form.end_time_1), (form.start_time_2, form.end_time_2))
    valid = True
    for start_field, end_field in ranges:
        if not (time(8, 0) <= start_field.data < end_field.data <= time(21, 0)):
            end_field.errors.append("Cada horario debe estar entre las 08:00 y las 21:00, con fin posterior al inicio.")
            valid = False
    if not valid:
        return None

    return "{} · {}–{} | {} · {}–{}".format(
        form.day_1.data, form.start_time_1.data.isoformat(timespec="minutes"), form.end_time_1.data.isoformat(timespec="minutes"),
        form.day_2.data, form.start_time_2.data.isoformat(timespec="minutes"), form.end_time_2.data.isoformat(timespec="minutes"),
    )


def _load_schedule_into_form(form: CourseForm, schedule: str) -> None:
    try:
        first, second = schedule.split(" | ")
        form.day_1.data, first_hours = first.split(" · ")
        form.day_2.data, second_hours = second.split(" · ")
        first_start, first_end = first_hours.split("–")
        second_start, second_end = second_hours.split("–")
        form.start_time_1.data, form.end_time_1.data = time.fromisoformat(first_start), time.fromisoformat(first_end)
        form.start_time_2.data, form.end_time_2.data = time.fromisoformat(second_start), time.fromisoformat(second_end)
    except (AttributeError, ValueError):
        try:
            days, hours = schedule.split(" · ")
            form.day_1.data, form.day_2.data = days.split(" y ")
            start, end = hours.split("–")
            form.start_time_1.data = form.start_time_2.data = time.fromisoformat(start)
            form.end_time_1.data = form.end_time_2.data = time.fromisoformat(end)
        except (AttributeError, ValueError):
            pass


def _require_instructor_or_admin():
    if current_user.role not in ("instructor", "admin"):
        abort(403)


def _require_course_owner_or_admin(course):
    if current_user.role == "admin":
        return
    if current_user.role != "instructor" or course.instructor_id != current_user.id:
        abort(403)


@courses_bp.route("/")
@login_required
def list_courses():
    courses = services.list_active_courses()
    enrolled_counts = {c.id: services.count_enrolled_for(c.id) for c in courses}
    return render_template("courses/list.html", courses=courses, enrolled_counts=enrolled_counts)


@courses_bp.route("/mine")
@login_required
def my_courses():
    _require_instructor_or_admin()
    courses = services.list_courses_by_instructor(current_user.id)
    enrolled_counts = {c.id: services.count_enrolled_for(c.id) for c in courses}
    return render_template("courses/my_courses.html", courses=courses, enrolled_counts=enrolled_counts)


@courses_bp.route("/<int:course_id>")
@login_required
def detail(course_id: int):
    course = services.get_course(course_id)
    if course is None:
        abort(404)
    enrolled_count = services.count_enrolled_for(course.id)

    students = None
    if current_user.role == "admin" or course.instructor_id == current_user.id:
        enrollments = list_enrollments_for_course(course.id)
        students = [get_user_by_id(e.user_id) for e in enrollments]

    return render_template(
        "courses/detail.html", course=course, enrolled_count=enrolled_count, students=students
    )


@courses_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    _require_instructor_or_admin()
    form = CourseForm()
    if not form.is_submitted():
        form.start_time_1.data = time(8, 0)
        form.end_time_1.data = time(10, 0)
        form.start_time_2.data = time(8, 0)
        form.end_time_2.data = time(10, 0)
    if form.validate_on_submit():
        schedule = _build_schedule(form)
        if schedule:
            services.create_course(
                title=form.title.data, description=form.description.data, capacity=form.capacity.data,
                instructor_id=current_user.id, classroom=form.classroom.data, schedule=schedule,
            )
            flash("Curso creado.", "success")
            return redirect(url_for("courses.list_courses"))
    return render_template("courses/form.html", form=form, mode="create")


@courses_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def edit(course_id: int):
    course = services.get_course(course_id)
    if course is None:
        abort(404)
    _require_course_owner_or_admin(course)

    form = CourseForm(obj=course)
    if not form.is_submitted():
        _load_schedule_into_form(form, course.schedule)
    if form.validate_on_submit():
        schedule = _build_schedule(form)
        if schedule:
            try:
                services.update_course(
                    course, title=form.title.data, description=form.description.data, capacity=form.capacity.data,
                    classroom=form.classroom.data, schedule=schedule,
                )
            except services.CapacityBelowEnrolledError as exc:
                flash(str(exc), "danger")
            else:
                flash("Curso actualizado.", "success")
                return redirect(url_for("courses.detail", course_id=course.id))

    return render_template("courses/form.html", form=form, mode="edit", course=course)


@courses_bp.route("/<int:course_id>/delete", methods=["POST"])
@login_required
def delete(course_id: int):
    course = services.get_course(course_id)
    if course is None:
        abort(404)
    _require_course_owner_or_admin(course)
    services.deactivate_course(course)
    flash("Curso desactivado.", "info")
    return redirect(url_for("courses.list_courses"))
