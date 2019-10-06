import flask
import json
from pprint import pprint
from .readClasses import Graph, Document, Idea

mod_read = flask.Blueprint('read', __name__, url_prefix='/read')


@mod_read.route('/graph')
def readGraph():
    graph = Graph()
    print("GET TOPICS")
    pprint(graph.trendingTopics()[0].data())
    docs = graph.data()
    pprint(docs)
    return json.dumps(docs)


@mod_read.route('/document/<docId>')
def readDocument(docId):
    doc = Document(docId).data()
    return json.dumps(doc)


@mod_read.route('/related-ideas/<ideaId>')
def findRelatedIdeas(ideaId):
    relatedIdeas = [i.data() for i in Idea(int(ideaId)).relatedIdeas()]
    print(relatedIdeas)
    return json.dumps(relatedIdeas)


@mod_read.route('/related-contents/<ideaId>')
def findRelatedContents(ideaId):
    relatedContents = [c.data() for c in Idea(int(ideaId)).relatedContents()]
    return json.dumps(relatedContents)
