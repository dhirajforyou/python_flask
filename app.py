import copy
import json
import logging
import os
from datetime import datetime

import json2table
from flask import Flask, request, jsonify, render_template, send_from_directory, g
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)
app = Flask(__name__)

# serve bootstrap resources from local.
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
if os.path.exists('static/js/lib/moment-with-locales.min.js'):
    # if momentjs present in the local, then serve it from local.
    app.config["local_moment"] = 'js/lib/moment-with-locales.min.js'
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


@app.route("/")
@app.route("/index.html")
@app.route("/hello/")
@app.route("/hello/<string:name>")
@app.route("/hello/<path:name>")
def say_hello(name=None):
    if name:
        logger.debug("Name found in the url")
    elif request.args.get("name"):
        logger.debug("Name taken from get param")
        name = request.args.get("name")
    else:
        name = "Stranger"
        logger.debug("Using default name %s " % name)

    toSend = get_data()
    template_data = {"name": name, "product": emit_html_table(toSend)}
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
