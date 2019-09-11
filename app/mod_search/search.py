import flask
import os
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
import json
import string
from pprint import pprint

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
            "docId": item["docId"]
        }
        documents.append(document)
    documents = json.dumps(documents)
    return documents


@mod_search.route('/document/<doc_id>')
def document(doc_id):
    docs = graph.run(
        "MATCH (n:Document {{docId:'{}'}}) RETURN n.title AS title, n.author AS author, n.lastModified AS lastModified, n.docId AS docId".format(doc_id)).data()
    doc = docs[0]
    document = {
        "title": doc["title"],
        "topics": ["Topic 1", "Topic 2", "Topic 3"],
        "author": doc["author"],
        "lastModified": doc["lastModified"],
        "docId": doc["docId"],
        "contents": []
    }
    contents = graph.run(
        "MATCH (d:Document {{docId:'{}'}})-[r]->(c:Content) RETURN id(c) AS id, c.level AS level, type(r) AS index".format(doc_id)).data()
    contents = sorted(contents, key=lambda k: int(k["index"]))
    for content in contents:
        newContent = {
            "id": content["id"],
            "level": content["level"],
            "ideas": []
        }
        ideas = graph.run(
            "MATCH (c:Content) WHERE id(c)= {} MATCH (c)-[r]->(i:Idea) RETURN id(i) AS id, i.text AS text, type(r) AS index".format(content["id"])).data()
        ideas = sorted(ideas, key=lambda k: int(k["index"]))
        for idea in ideas:
            newIdea = {
                "id": idea["id"],
                "text": idea["text"],
                "entities": [],
                "lemmas": []
            }
            entities = graph.run(
                "MATCH (i:Idea) WHERE id(i)= {} MATCH (i)-[r]->(e:Entity) RETURN id(e) AS id, e.name AS name, e.entType AS entType".format(idea["id"])).data()
            for entity in entities:
                if entity not in newIdea["entities"]:
                    newIdea["entities"].append(entity)
            lemmas = graph.run(
                "MATCH (i:Idea) WHERE id(i)= {} MATCH (i)-[r]->(l:Lemma) RETURN id(l) AS id, l.name AS name, l.pos AS pos".format(idea["id"])).data()
            for lemma in lemmas:
                if lemma not in newIdea["lemmas"]:
                    newIdea["lemmas"].append(lemma)
            newContent["ideas"].append(newIdea)
        document["contents"].append(newContent)
    return(document)
