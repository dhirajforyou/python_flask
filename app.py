from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello world"


@app.route("/hello/")
@app.route("/hello/<string:name>")
@app.route("/hello/<path:name>")
def sayHello(name=None):
    if name:
        return "Hello {}".format(name)
    if request.args.get("name"):
        name = request.args.get("name")
    else:
        name = "Stranger"
    return "Hello {}".format(name)


if __name__ == "__main__":
    app.run(debug=True)
