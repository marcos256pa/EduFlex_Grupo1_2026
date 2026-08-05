from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CourseOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructor_id: int
    capacity: int
    classroom: str = ""
    schedule: str = ""
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    capacity: int = 30
    classroom: str = Field(min_length=1, max_length=120)
    schedule: str = Field(min_length=1, max_length=160)


class CourseUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    capacity: int
    classroom: str = Field(min_length=1, max_length=120)
    schedule: str = Field(min_length=1, max_length=160)
