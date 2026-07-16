from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    full_name = StringField("Nombre completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField(
        "Rol",
        choices=[("student", "Estudiante"), ("instructor", "Docente")],
        default="student",
    )
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(), EqualTo("password", message="Las contraseñas no coinciden")],
    )
    submit = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")
