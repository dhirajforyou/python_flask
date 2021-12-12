from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class Nameform(FlaskForm):
    name = StringField("What is your name", validators=[DataRequired()], render_kw={'autofocus': True})
    # checkmode = RadioField('checkmode', validators=[DataRequired()],
    # choices=[('in', 'Check-In'), ('out', 'Check-Out')])
    submit = SubmitField("Submit")
