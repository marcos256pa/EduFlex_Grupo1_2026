from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.modules.users import services
from app.modules.users.schemas import LoginForm, RegisterForm

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("courses.list_courses"))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = services.create_user(
                full_name=form.full_name.data,
                email=form.email.data,
                password=form.password.data,
                role=form.role.data,
            )
        except services.EmailAlreadyExistsError as exc:
            flash(str(exc), "danger")
        else:
            login_user(user)
            flash("Cuenta creada correctamente.", "success")
            return redirect(url_for("courses.list_courses"))

    return render_template("users/register.html", form=form)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("courses.list_courses"))

    form = LoginForm()
    if form.validate_on_submit():
        user = services.authenticate(form.email.data, form.password.data)
        if user is None:
            flash("Correo o contraseña incorrectos.", "danger")
        else:
            login_user(user)
            return redirect(url_for("courses.list_courses"))

    return render_template("users/login.html", form=form)


@users_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/")
@login_required
def list_users():
    if current_user.role != "admin":
        abort(403)
    all_users = services.list_users()
    return render_template("users/list.html", users=all_users)
