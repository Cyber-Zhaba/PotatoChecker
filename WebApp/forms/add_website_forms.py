from flask_wtf import FlaskForm
from wtforms import StringField, URLField
from wtforms.validators import DataRequired


class AddWebsiteForm(FlaskForm):
    name = StringField('Website name', validators=[DataRequired()])
    link = URLField('Link', validators=[DataRequired()])
