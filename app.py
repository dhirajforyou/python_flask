
import logging
import os
from datetime import datetime
from threading import Thread

from flask import Flask, jsonify, render_template, send_from_directory, g, session, redirect, url_for, flash, \
    copy_current_request_context
from flask_bootstrap import Bootstrap
from flask_mail import Message, Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.exceptions import HTTPException
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired

logger = logging.getLogger(__name__)
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# serve bootstrap resources from local.
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
if os.path.exists('static/js/lib/moment-with-locales.min.js'):
    # if momentjs present in the local, then serve it from local.
    app.config["local_moment"] = 'js/lib/moment-with-locales.min.js'

app.config["SECRET_KEY"] = "shhhh... its private."

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_ADMIN"] = os.environ.get("MAIL_ADMIN")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_SUBJECT_PREFIX"] = "[My Application]"
app.config["MAIL_SENDER"] = "My Application <no-reply@gmail.com>"

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


def create_message(to, subject, template, **kwargs):
    logger.info("Sending to %s" % to)
    recipients = to if isinstance(to, list) else [to]
    msg = Message(app.config.get("MAIL_SUBJECT_PREFIX") + subject,
                  sender=app.config["MAIL_SENDER"], recipients=recipients)
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    return msg


def send_email(to, subject, template, **kwargs):
    # Send mail in sync
    message = create_message(to, subject, template, **kwargs)
    logger.debug("Prepared mail message")
    mail.send(message)
    logger.debug("Sent mail")


def send_async_mail(to, subject, template, **kwargs):
    # send mail in async
    message = create_message(to, subject, template, **kwargs)
    logger.debug("Prepared mail message")

    # copy_current_request_context will add app context
    @copy_current_request_context
    def send_message(message):
        mail.send(message)
        logger.debug("Mail sent")

    sender = Thread(name='mail_sender', target=send_message, args=(message,))
    sender.start()
    logger.debug("Thread started")


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


class Nameform(FlaskForm):
    name = StringField("What is your name", validators=[DataRequired()], render_kw={'autofocus': True})
    # checkmode = RadioField('checkmode', validators=[DataRequired()],
    # choices=[('in', 'Check-In'), ('out', 'Check-Out')])
    submit = SubmitField("Submit")


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return "<Role: %r>" % self.name


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return "<User %r>" % self.username


@app.route("/", methods=['GET', 'POST'])
def index():
    form = Nameform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if not user:
            user = User(username=form.name.data)
            db.session.add(user)
            session["known"] = False
            send_async_mail(app.config["MAIL_ADMIN"], "New User", "mail/new_user", user=user)
            logger.debug("mail part completed")
        else:
            session["known"] = True
        old_name = session.get("name")
        if old_name:
            if old_name != form.name.data:
                flash("Hmm... Looks like you have changed your name.", 'warning')
            else:
                flash("Glad to see you again... !", 'info')
        session["name"] = form.name.data
        # session["checkmode"] = form.checkmode.data
        form.name.data = ''
        # form.checkmode.data = ''
        return redirect(url_for('index'))
    template_data = {"name": session.get("name", "Stranger"),
                     "known": session.get("known", False),
                     # "checkmode": session.get("checkmode", None),
                     "form": form}
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
