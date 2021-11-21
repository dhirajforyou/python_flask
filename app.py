import copy
import json
import logging
import os
from datetime import datetime

import json2table
from flask import Flask, request, jsonify, render_template, send_from_directory
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


@app.route("/favicon.ico")
def favicon():
    # return redirect(url_for('static', filename='images/network-scale-blue.svg'))
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.png')


@app.route("/")
@app.route("/index.html")
def index():
    message = "Hello world"
    agent = request.headers.get("User-Agent")
    toSend = get_data()
    toSend["lang"] = request.headers.get('Accept-Language')
    template_data = {"message": message, "agent": agent, "product": emit_html_table(toSend), "app": app,
                     "current_time": datetime.utcnow()}
    return render_template("index.html", **template_data)


@app.route("/hello/")
@app.route("/hello/<string:name>")
@app.route("/hello/<path:name>")
def say_hello(name=None):
    if name:
        logger.debug("Name found in the url")
        return "Hello {}".format(name)
    if request.args.get("name"):
        logger.debug("Name taken from get param")
        name = request.args.get("name")
    else:
        name = "Stranger"
        logger.debug("Using default name %s " % name)
    return "Hello {}".format(name)


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
