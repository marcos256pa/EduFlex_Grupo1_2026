from app.modules.courses.services import list_courses_by_instructor
from app.modules.enrollments.services import count_active_enrollments_for_course
 
def get_dashboard_summary(instructor_id: int):
    courses = list_courses_by_instructor(instructor_id)
 
    total_courses = len(courses)
    total_students = 0
    total_percentage = 0
 
    for course in courses:
        enrolled = count_active_enrollments_for_course(course.id)
        total_students += enrolled
 
        if course.capacity > 0:
            total_percentage += (enrolled / course.capacity) * 100
 
    average = round(total_percentage / total_courses) if total_courses else 0
 
    return {
        "courses": total_courses,
        "students": total_students,
        "occupancy": average,
    }
 
 
def get_course_report(instructor_id: int):
    courses = list_courses_by_instructor(instructor_id)
 
    report = []
 
    for course in courses:
 
        enrolled = count_active_enrollments_for_course(course.id)
 
        percentage = round((enrolled / course.capacity) * 100) if course.capacity else 0
 
        if percentage == 100:
            status = "Completo"
        elif percentage >= 70:
            status = "Casi lleno"
        else:
            status = "Disponible"
 
        report.append(
            {
                "title": course.title,
                "capacity": course.capacity,
                "enrolled": enrolled,
                "occupancy": percentage,
                "status": status,
            }
        )
 
    return report