from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class SpiderFormAdd(FlaskForm):
    name = StringField('Название паука', validators=[DataRequired()])
    size = StringField('Размеры паука', validators=[DataRequired()])
    color = StringField('Цвет паука', validators=[DataRequired()])
    Spider_type = RadioField('Тип паука', validators=[DataRequired()], choices=['Охотник', 'Тенетник'])
    time = RadioField('Время активности', validators=[DataRequired()], choices=['День', 'Ночь'])
    submit = SubmitField('Подтвердить')