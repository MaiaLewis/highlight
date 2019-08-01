import flask
from app.mod_auth.routes import mod_auth as auth_module

app = flask.Flask(__name__, static_folder="../build/static",
                  template_folder="../build")
app.secret_key = "secret"
app.register_blueprint(auth_module)


@app.route('/')
def index():
    return flask.render_template("index.html")
