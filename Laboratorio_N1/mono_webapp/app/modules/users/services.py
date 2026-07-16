from app.database import db
from app.modules.users.models import User


class EmailAlreadyExistsError(Exception):
    pass


def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def get_user_by_email(email: str) -> User | None:
    return db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()


def create_user(full_name: str, email: str, password: str, role: str = "student") -> User:
    if get_user_by_email(email) is not None:
        raise EmailAlreadyExistsError(f"Ya existe un usuario con el correo {email}")

    user = User(full_name=full_name, email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User | None:
    user = get_user_by_email(email)
    if user is None or not user.check_password(password):
        return None
    return user


def list_users() -> list[User]:
    return db.session.execute(db.select(User).order_by(User.created_at.desc())).scalars().all()
