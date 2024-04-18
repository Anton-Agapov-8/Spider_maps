from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = PasswordField('Название паука', validators=[DataRequired()])
    size = PasswordField('Размеры паука', validators=[DataRequired()])
    color = PasswordField('Цвет паука', validators=[DataRequired()])
    Spider_type = RadioField('Тип паука', validators=[DataRequired()], validate_choice=['Охотник', 'Тенетник'])
    time = RadioField('Время активности', validators=[DataRequired()], validate_choice=['День', 'Ночь'])
    submit = SubmitField('Подтвердить')