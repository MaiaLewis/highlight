import flask
import json
import string

mod_auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


@mod_auth.route('/search')
def search():
    documents = [{
        "title": "TITLE",
        "topics": ["Topic 1", "Topic 2", "Topic 3"],
        "author": "AUTHOR",
        "last_edit": "DATE"
    }]
    documents = json.dumps(documents)
    return documents
