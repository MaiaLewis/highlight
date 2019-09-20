import flask
# for local development use:
# from app.mod_auth.authLocalRoutes import mod_auth as auth_module
from app.mod_auth.authRoutes import mod_auth as auth_module
from app.mod_write.writeRoutes import mod_write as write_module
from app.mod_read.readRoutes import mod_read as read_module
from flask_cors import CORS

app = flask.Flask(__name__, static_folder="../build/static",
                  template_folder="../build")


# remove CORS once App is out of dev
CORS(app)
app.secret_key = "secret"
app.register_blueprint(auth_module)
app.register_blueprint(write_module)
app.register_blueprint(read_module)


@app.route('/')
def index():
    return flask.render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
