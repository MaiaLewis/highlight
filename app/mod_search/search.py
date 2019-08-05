import flask
import os
from neo4j.v1 import GraphDatabase, basic_auth
import json
import string

mod_search = flask.Blueprint('search', __name__, url_prefix='/search')

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


@mod_search.route('/search')
def search():
    session = driver.session()  # pylint: disable=assignment-from-no-return
    items = session.run(
        "MATCH (n:Document) RETURN n.title AS title, n.author AS author, n.last_edit AS last_edit")
    documents = []
    for item in items:
        document = {
            "title": item["title"],
            "topics": ["Topic 1", "Topic 2", "Topic 3"],
            "author": item["author"],
            "last_edit": item["last_edit"]
        }
        documents.append(document)
    session.close()
    documents = json.dumps(documents)
    return documents
