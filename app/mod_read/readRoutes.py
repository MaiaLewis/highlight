import flask
import os
from neo4j.v1 import GraphDatabase, basic_auth
import json
import string
from pprint import pprint
from .readClasses import Document, Idea

mod_read = flask.Blueprint('read', __name__, url_prefix='/read')

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


@mod_read.route('/graph')
def readGraph():
    graph = driver.session()  # pylint: disable=assignment-from-no-return
    items = graph.run(
        "MATCH (d:Document)-[:Topic]->(n) RETURN d.title AS title, d.author AS author, d.lastModified AS lastModified, d.docId AS docId, COLLECT(n.name) AS topics")
    documents = []
    for item in items:
        document = {
            "title": item["title"],
            "topics": item["topics"][-5:],
            "author": item["author"],
            "lastModified": item["lastModified"],
            "docId": item["docId"],
        }
        documents.append(document)
    graph.close()
    return json.dumps(documents)


@mod_read.route('/document/<docId>')
def readDocument(docId):
    doc = Document(docId).data()
    return json.dumps(doc)


@mod_read.route('/related-ideas/<ideaId>')
def findRelatedIdeas(ideaId):
    relatedIdeas = [i.data() for i in Idea(int(ideaId)).relatedIdeas()]
    return json.dumps(relatedIdeas)


@mod_read.route('/related-contents/<ideaId>')
def findRelatedContents(ideaId):
    relatedContents = [c.data() for c in Idea(int(ideaId)).relatedContents()]
    return json.dumps(relatedContents)
