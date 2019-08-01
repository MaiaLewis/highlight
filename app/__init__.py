import flask
from app.mod_auth.routes import mod_auth as auth_module
from flask_cors import CORS

app = flask.Flask(__name__, static_folder="../build/static",
                  template_folder="../build")
CORS(app)
app.secret_key = "secret"
app.register_blueprint(auth_module)


@app.route('/')
def index():
    print("got this far")
    return flask.render_template("index.html")
