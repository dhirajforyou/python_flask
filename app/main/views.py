import os
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, current_app as app, send_from_directory, g
import logging
from . import main
from .forms import Nameform
from .. import db
from ..models import User
from ..email import send_async_mail
logger = logging.getLogger(__name__)


@main.before_request
def before_request():
    # time.time() will give epoch time, which momentjs will give error to parse
    g.request_start_time = datetime.utcnow()  # time.time()
    # creates a function that returns the time since before_request was called.
    # The function is called later when any template is rendered (ex. in index.html)
    # which happens after the request has completed.
    # g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@main.route("/favicon.ico")
def favicon():
    # return redirect(url_for('static', filename='images/network-scale-blue.svg'))
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.png')


@main.route('/', methods=['GET', 'POST'])
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