from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.modules.courses import services as courses_services
from app.modules.enrollments import services

enrollments_bp = Blueprint("enrollments", __name__, url_prefix="/enrollments")


@enrollments_bp.route("/")
@login_required
def my_enrollments():
    my_enr = services.list_enrollments_for_user(current_user.id)
    courses_by_id = {e.course_id: courses_services.get_course(e.course_id) for e in my_enr}
    return render_template("enrollments/list.html", enrollments=my_enr, courses_by_id=courses_by_id)


@enrollments_bp.route("/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll(course_id: int):
    try:
        services.enroll_user(current_user.id, course_id)
        flash("Te inscribiste correctamente.", "success")
    except services.AlreadyEnrolledError as exc:
        flash(str(exc), "warning")
    except services.CourseFullError as exc:
        flash(str(exc), "danger")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(request.referrer or url_for("courses.list_courses"))


@enrollments_bp.route("/<int:course_id>/cancel", methods=["POST"])
@login_required
def cancel(course_id: int):
    try:
        services.cancel_enrollment(current_user.id, course_id)
        flash("Inscripción cancelada.", "info")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(request.referrer or url_for("enrollments.my_enrollments"))
