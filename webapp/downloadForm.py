from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DecimalField, RadioField
from wtforms.validators import DataRequired, Required


class DownloadForm(FlaskForm):
    default_type = 'N'
    type = RadioField('Type', choices=[('N', 'New activities'), ('L', 'Fixed number of latest activities'),],
                                       default=default_type, validators=[DataRequired()])
    nr_of_latest = IntegerField()
    submit = SubmitField('Download')
