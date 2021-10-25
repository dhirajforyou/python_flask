from flask import Flask, request
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    return "Hello world"


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
