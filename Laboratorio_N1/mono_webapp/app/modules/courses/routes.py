from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.modules.courses import services
from app.modules.courses.schemas import CourseForm
from app.modules.enrollments.services import list_enrollments_for_course
from app.modules.users.services import get_user_by_id

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


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
    if form.validate_on_submit():
        services.create_course(
            title=form.title.data,
            description=form.description.data,
            capacity=form.capacity.data,
            instructor_id=current_user.id,
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
    if form.validate_on_submit():
        try:
            services.update_course(
                course,
                title=form.title.data,
                description=form.description.data,
                capacity=form.capacity.data,
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
