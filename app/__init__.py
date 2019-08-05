import flask
from app.mod_auth.auth import mod_auth as auth_module
from app.mod_save.save import mod_save as save_module
from app.mod_search.search import mod_search as search_module
from flask_cors import CORS

app = flask.Flask(__name__, static_folder="../build/static",
                  template_folder="../build")
# remove CORS once App is out of dev
CORS(app)
app.secret_key = "secret"
app.register_blueprint(auth_module)
app.register_blueprint(save_module)
app.register_blueprint(search_module)


@app.route('/')
def index():
    print("got this far")
    return flask.render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
