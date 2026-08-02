from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, NumberRange


class CourseForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripción", validators=[Length(max=2000)])
    capacity = IntegerField(
        "Cupos disponibles", validators=[DataRequired(), NumberRange(min=1, max=500)], default=30
    )
    classroom = StringField("Aula", validators=[DataRequired(), Length(max=120)])
    day_1 = SelectField("Primer día", choices=[(day, day) for day in ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")], validators=[DataRequired()], default="Lunes")
    day_2 = SelectField("Segundo día", choices=[(day, day) for day in ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")], validators=[DataRequired()], default="Miércoles")
    start_time = TimeField("Hora de inicio", format="%H:%M", validators=[DataRequired()])
    end_time = TimeField("Hora de fin", format="%H:%M", validators=[DataRequired()])
    submit = SubmitField("Guardar")
