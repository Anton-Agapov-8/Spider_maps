from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SpiderFormUpdate(FlaskForm):
    name = StringField('Название паука', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')