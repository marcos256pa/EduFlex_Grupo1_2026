from app.database import db
from app.modules.courses import services as courses_services
from app.modules.enrollments.models import Enrollment


class AlreadyEnrolledError(Exception):
    pass


class CourseFullError(Exception):
    pass


def count_active_enrollments_for_course(course_id: int) -> int:
    return db.session.execute(
        db.select(db.func.count(Enrollment.id)).filter_by(course_id=course_id, status="active")
    ).scalar_one()


def get_enrollment(user_id: int, course_id: int) -> Enrollment | None:
    return db.session.execute(
        db.select(Enrollment).filter_by(user_id=user_id, course_id=course_id, status="active")
    ).scalar_one_or_none()


def get_any_enrollment(user_id: int, course_id: int) -> Enrollment | None:
    return db.session.execute(
        db.select(Enrollment).filter_by(user_id=user_id, course_id=course_id)
    ).scalar_one_or_none()


def enroll_user(user_id: int, course_id: int) -> Enrollment:
    course = courses_services.get_course(course_id)
    if course is None or not course.is_active:
        raise ValueError("El curso no existe o no está activo")

    existing = get_any_enrollment(user_id, course_id)
    if existing is not None and existing.status == "active":
        raise AlreadyEnrolledError("Ya estás inscrito en este curso")

    current_count = count_active_enrollments_for_course(course_id)
    if current_count >= course.capacity:
        raise CourseFullError("El curso ya alcanzó su cupo máximo")

    if existing is not None:
        existing.status = "active"
        db.session.commit()
        return existing

    enrollment = Enrollment(user_id=user_id, course_id=course_id, status="active")
    db.session.add(enrollment)
    db.session.commit()
    return enrollment


def cancel_enrollment(user_id: int, course_id: int) -> None:
    enrollment = get_enrollment(user_id, course_id)
    if enrollment is None:
        raise ValueError("No existe una inscripción activa para cancelar")
    enrollment.status = "cancelled"
    db.session.commit()


def cancel_all_for_course(course_id: int) -> None:
    enrollments = list_enrollments_for_course(course_id)
    for enrollment in enrollments:
        enrollment.status = "cancelled"
    db.session.commit()


def list_enrollments_for_user(user_id: int) -> list[Enrollment]:
    return db.session.execute(
        db.select(Enrollment).filter_by(user_id=user_id, status="active")
    ).scalars().all()


def list_enrollments_for_course(course_id: int) -> list[Enrollment]:
    return db.session.execute(
        db.select(Enrollment).filter_by(course_id=course_id, status="active")
    ).scalars().all()
