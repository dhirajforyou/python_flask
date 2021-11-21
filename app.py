import copy
import json
import logging
import os
from datetime import datetime

import json2table
from flask import Flask, request, jsonify, render_template, send_from_directory, g
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from werkzeug.exceptions import HTTPException
from wtforms import StringField, SubmitField
from wtforms.validators import Required

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

data = json.load(open("data.json"))


def get_data():
    return copy.deepcopy(data)


def emit_html_table(json_object):
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:100%"}
    html = json2table.convert(json_object, build_direction=build_direction,
                              table_attributes=table_attributes)
    return html


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
    name = StringField("What is your name", validators=[Required()], render_kw={'autofocus': True})
    submit = SubmitField("Submit")


@app.route("/", methods=['GET', 'POST'])
@app.route("/index.html", methods=['GET', 'POST'])
@app.route("/hello/", methods=['GET', 'POST'])
@app.route("/hello/<string:name>", methods=['GET', 'POST'])
@app.route("/hello/<path:name>", methods=['GET', 'POST'])
def say_hello(name=None):
    if name:
        logger.debug("Name found in the url")
    elif request.args.get("name"):
        logger.debug("Name taken from get param")
        name = request.args.get("name")
    else:
        name = "Stranger"
        logger.debug("Using default name %s " % name)
    form = Nameform()
    if form.validate_on_submit():
        user_name = form.name.data
        form.name.data = ''
        if user_name:
            name = user_name
    template_data = {"name": name, "form": form}
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
