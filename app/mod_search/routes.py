import flask
import json
import string

mod_search = flask.Blueprint('search', __name__, url_prefix='/search')


@mod_search.route('/search')
def search():
    documents = [{
        "title": "TITLE",
        "topics": ["Topic 1", "Topic 2", "Topic 3"],
        "author": "AUTHOR",
        "last_edit": "DATE"
    }]
    documents = json.dumps(documents)
    return documents
