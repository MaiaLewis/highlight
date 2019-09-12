import flask
import os
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
import json
import string
from pprint import pprint
from .readClasses import Document, Idea

mod_search = flask.Blueprint('search', __name__, url_prefix='/search')

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

graph = Graph(graphenedb_url, user=graphenedb_user, password=graphenedb_pass,
              bolt=True, secure=True, http_port=24789, https_port=24780)


@mod_search.route('/search')
def search():
    items = graph.run(
        "MATCH (n:Document) RETURN n.title AS title, n.author AS author, n.lastModified AS lastModified, n.docId AS docId")
    documents = []
    for item in items:
        document = {
            "title": item["title"],
            "topics": ["Topic 1", "Topic 2", "Topic 3"],
            "author": item["author"],
            "lastModified": item["lastModified"],
            "docId": item["docId"],
        }
        documents.append(document)
    return json.dumps(documents)


@mod_search.route('/document/<docId>')
def document(docId):
    doc = Document(docId).data()
    return json.dumps(doc)


@mod_search.route('/info/<ideaId>')
def infoSearch(ideaId):
    relatedIdeas = [i.data() for i in Idea(int(ideaId)).relatedIdeas()]
    # relatedContents = [c.data() for c in Idea(int(ideaId)).relatedContents()]
    # pprint(relatedContents)
    return json.dumps(relatedIdeas)
