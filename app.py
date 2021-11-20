from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import HTTPException
from flask_bootstrap import Bootstrap
import json
import json2table
import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)

# serve bootstrap resources from local.
app.config["BOOTSTRAP_SERVE_LOCAL"] = True

bootstrap = Bootstrap(app)

# sample product data
data = json.load(open("data.json"))


def emit_html_table(json_object):
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:100%"}
    html = json2table.convert(json_object, build_direction=build_direction,
                              table_attributes=table_attributes)
    return html


@app.route("/")
@app.route("/index.html")
def index():
    message = "Hello world"
    agent = request.headers.get("User-Agent")
    template_data = {"message": message, "agent": agent, "product": emit_html_table(data)}
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
