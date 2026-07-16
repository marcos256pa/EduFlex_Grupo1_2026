from datetime import datetime, timezone

from app.database import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="active")
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Enrollment user={self.user_id} course={self.course_id} status={self.status}>"
