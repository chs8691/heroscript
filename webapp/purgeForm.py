from flask_wtf import FlaskForm
from wtforms import SubmitField


class PurgeForm(FlaskForm):
    style_button = {'class': 'submit-button'}

    submit = SubmitField('SUBMIT', render_kw=style_button)
