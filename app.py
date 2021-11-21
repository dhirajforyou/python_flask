
import logging
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, send_from_directory, g, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from werkzeug.exceptions import HTTPException
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired

logger = logging.getLogger(__name__)
app = Flask(__name__)

# serve bootstrap resources from local.
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
if os.path.exists('static/js/lib/moment-with-locales.min.js'):
    # if momentjs present in the local, then serve it from local.
    app.config["local_moment"] = 'js/lib/moment-with-locales.min.js'

app.config["SECRET_KEY"] = "shhhh... its private."
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.before_request
def before_request():
    # time.time() will give epoch time, which momentjs will give error to parse
    g.request_start_time = datetime.utcnow()  # time.time()
    # creates a function that returns the time since before_request was called.
    # The function is called later when any template is rendered (ex. in index.html)
    # which happens after the request has completed.
    # g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.route("/favicon.ico")
def favicon():
    # return redirect(url_for('static', filename='images/network-scale-blue.svg'))
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.png')


class Nameform(Form):
    name = StringField("What is your name", validators=[DataRequired()], render_kw={'autofocus': True})
    checkmode = RadioField('checkmode', validators=[DataRequired()], choices=[('in', 'Check-In'), ('out', 'Check-Out')])
    submit = SubmitField("Submit")


@app.route("/", methods=['GET', 'POST'])
def index():
    form = Nameform()
    name = "Stranger"
    checkmode = None
    if form.validate_on_submit():
        session["name"] = form.name.data
        session["checkmode"] = form.checkmode.data
        return redirect(url_for('index'))
    template_data = {"name": session.get("name"), "checkmode": session.get("checkmode", None), "form": form}
    return render_template("user.html", **template_data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(Exception)
def handle_error(e):
    logger.debug("Exception %s" % e)
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
