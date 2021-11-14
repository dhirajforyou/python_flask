from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/")
@app.route("/index.html")
def index():
    message = "Hello world"
    agent = request.headers.get("User-Agent")
    return render_template("index.html", message=message, agent=agent)


@app.route("/hello/")
@app.route("/hello/<string:name>")
@app.route("/hello/<path:name>")
def sayHello(name=None):
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
