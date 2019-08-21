import flask
import os
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
import json
import string

mod_search = flask.Blueprint('search', __name__, url_prefix='/search')

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

graph = Graph(graphenedb_url, user=graphenedb_user, password=graphenedb_pass,
              bolt=True, secure=True, http_port=24789, https_port=24780)


@mod_search.route('/search')
def search():
    items = graph.run(
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
    documents = json.dumps(documents)
    return documents
