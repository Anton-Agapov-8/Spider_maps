from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class SpiderFormUpdate(FlaskForm):
    spider_names = open('Spider_names.txt', 'r', encoding='utf8')
    choice = list(spider_names.read().split('|'))
    name = SelectField('Название паука', validators=[DataRequired()], choices=choice)
    submit = SubmitField('Подтвердить')

