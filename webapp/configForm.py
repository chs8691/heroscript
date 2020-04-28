from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class ConfigForm(FlaskForm):

    style_button = {'class': 'submit-button'}

    port = IntegerField('port')
    load_dir = StringField('load_dir')
    archive_dir = StringField('archive_dir')
    velohero_sso_id = StringField('velohero_sso_id', validators=[DataRequired()])
    strava_client_id = StringField('strava_client_id', validators=[DataRequired()])
    strava_description__BY__strava_name = StringField('strava_description__BY__strava_name')
    strava_description__BY__training_type = StringField('strava_description__BY__training_type')
    garmin_connect_username = StringField('garmin_connect_username')
    garmin_connect_password = StringField('garmin_connect_password')
    strava_reset = BooleanField('strava_reset')
    submit = SubmitField('SAVE', render_kw=style_button)
