from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired, Length, NumberRange


class CourseForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripción", validators=[Length(max=2000)])
    capacity = IntegerField(
        "Cupos disponibles", validators=[DataRequired(), NumberRange(min=1, max=500)], default=30
    )
    submit = SubmitField("Guardar")
