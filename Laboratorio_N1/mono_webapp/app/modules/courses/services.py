from app.database import db
from app.modules.courses.models import Course


def list_active_courses() -> list[Course]:
    return db.session.execute(
        db.select(Course).filter_by(is_active=True).order_by(Course.created_at.desc())
    ).scalars().all()


def list_courses_by_instructor(instructor_id: int) -> list[Course]:
    return db.session.execute(
        db.select(Course).filter_by(instructor_id=instructor_id).order_by(Course.created_at.desc())
    ).scalars().all()


def get_course(course_id: int) -> Course | None:
    return db.session.get(Course, course_id)


def create_course(title: str, description: str, capacity: int, instructor_id: int) -> Course:
    course = Course(
        title=title,
        description=description,
        capacity=capacity,
        instructor_id=instructor_id,
    )
    db.session.add(course)
    db.session.commit()
    return course


class CapacityBelowEnrolledError(Exception):
    pass


def update_course(course: Course, title: str, description: str, capacity: int) -> Course:
    enrolled_count = count_enrolled_for(course.id)
    if capacity < enrolled_count:
        raise CapacityBelowEnrolledError(
            f"El cupo no puede ser menor a {enrolled_count}, la cantidad de estudiantes ya matriculados"
        )

    course.title = title
    course.description = description
    course.capacity = capacity
    db.session.commit()
    return course


def deactivate_course(course: Course) -> None:
    from app.modules.enrollments.services import cancel_all_for_course

    course.is_active = False
    db.session.commit()
    cancel_all_for_course(course.id)


def count_enrolled_for(course_id: int) -> int:
    from app.modules.enrollments.services import count_active_enrollments_for_course

    return count_active_enrollments_for_course(course_id)
