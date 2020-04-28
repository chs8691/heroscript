from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class TransferForm(FlaskForm):

    style_button = {'class': 'submit-button'}

    strava = BooleanField('strava')
    velohero = BooleanField('velohero')
    archive = BooleanField('archive')
    submit = SubmitField('SUBMIT', render_kw=style_button)
