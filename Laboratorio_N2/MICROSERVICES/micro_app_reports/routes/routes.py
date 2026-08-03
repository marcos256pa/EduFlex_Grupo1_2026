import asyncio
import os
from typing import Any

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

USERS_URL = os.getenv("USERS_URL", "http://micro_app_user:8001")
COURSES_URL = os.getenv("COURSES_URL", "http://micro_app_courses:8002")
ENROLLMENTS_URL = os.getenv("ENROLLMENTS_URL", "http://micro_app_enrollments:8003")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))

reports_router = APIRouter()
bearer = HTTPBearer()


def decode_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict[str, Any]:
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token.") from exc


def require_instructor_or_admin(token: dict[str, Any]) -> None:
    if token.get("role") not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Access denied.")


def report_status(occupancy: int) -> str:
    if occupancy >= 100:
        return "Completo"
    if occupancy >= 70:
        return "Casi lleno"
    return "Disponible"


@reports_router.get("/overview")
async def overview(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    token: dict[str, Any] = Depends(decode_token),
) -> dict[str, Any]:
    require_instructor_or_admin(token)
    headers = {"Authorization": f"Bearer {credentials.credentials}"}

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            user_response, courses_response = await asyncio.gather(
                client.get(f"{USERS_URL}/api/users/{token['sub']}", headers=headers),
                client.get(f"{COURSES_URL}/api/courses/mine", headers=headers),
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Source services are unavailable.") from exc

    if user_response.status_code != 200:
        raise HTTPException(status_code=502, detail="User service returned an invalid response.")
    if courses_response.status_code != 200:
        raise HTTPException(status_code=502, detail="Course service returned an invalid response.")

    user = user_response.json()
    courses = courses_response.json()
    if not isinstance(courses, list):
        raise HTTPException(status_code=502, detail="Course service returned an invalid payload.")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            enrollment_responses = await asyncio.gather(
                *[
                    client.get(
                        f"{ENROLLMENTS_URL}/api/enrollments/course/{course['id']}/count",
                        headers=headers,
                    )
                    for course in courses
                ]
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Enrollment service is unavailable.") from exc

    reports = []
    total_students = 0
    total_occupancy = 0
    for course, enrollment_response in zip(courses, enrollment_responses):
        enrolled = enrollment_response.json().get("count", 0) if enrollment_response.status_code == 200 else 0
        capacity = course.get("capacity", 0)
        occupancy = round((enrolled / capacity) * 100) if capacity else 0
        total_students += enrolled
        total_occupancy += occupancy
        reports.append(
            {
                "course_id": course.get("id"),
                "title": course.get("title", "Sin titulo"),
                "classroom": course.get("classroom", "Sin aula asignada"),
                "schedule": course.get("schedule", "Horario pendiente"),
                "capacity": capacity,
                "enrolled": enrolled,
                "occupancy": occupancy,
                "status": report_status(occupancy),
            }
        )

    return {
        "instructor": {"id": user.get("id", int(token["sub"])), "full_name": user.get("full_name", "")},
        "summary": {
            "courses": len(courses),
            "students": total_students,
            "occupancy": round(total_occupancy / len(courses)) if courses else 0,
        },
        "reports": reports,
    }
