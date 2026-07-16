from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    ROLE_LABELS = {
        "student": "Estudiante",
        "instructor": "Docente",
        "admin": "Administrador",
    }

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def role_label(self):
        return self.ROLE_LABELS.get(self.role, self.role)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
