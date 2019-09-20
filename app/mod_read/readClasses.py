from neo4j.v1 import GraphDatabase, basic_auth
import json
import os

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


class Document:
    def __init__(self, docId):
        self.docId = docId
        self.title = None
        self.author = None
        self.lastModified = None
        self.contents = self.getContents()

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        document = graph.run(
            "MATCH (n:Document {{docId:'{}'}}) RETURN n.title AS title, n.author AS author, n.lastModified AS lastModified".format(self.docId)).data()[0]
        graph.close()
        self.title = document["title"]
        self.author = document["author"]
        self.lastModified = document["lastModified"]

    def getContents(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        contents = graph.run(
            "MATCH (d:Document {{docId:'{}'}})-[r]->(c:Content) RETURN id(c) AS id, TYPE(r) as index".format(self.docId)).data()
        graph.close()
        contents = sorted(contents, key=lambda k: int(k["index"]))
        for content in contents:
            content = Content(content["id"])
            yield content

    def data(self):
        document = {
            "id": self.docId,
            "title": self.title,
            "author": self.author,
            "lastModified": self.lastModified,
            "contents": [c.data() for c in self.contents]
        }
        return document


class Content:
    def __init__(self, contId):
        self.contId = contId
        self.level = None
        self.parents = None
        self.ideas = self.getIdeas()

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        content = graph.run(
            "MATCH (c:Content)<--(d:Document) WHERE ID(c)={} RETURN c.level AS level, COLLECT(d.docId) AS parents".format(self.contId)).data()[0]
        graph.close()
        self.level = content["level"]
        self.parents = content["parents"]

    def getIdeas(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        ideas = graph.run(
            "MATCH (c:Content)-[r]->(i:Idea) WHERE ID(c)={} RETURN id(i) AS id, TYPE(r) AS index".format(self.contId)).data()
        graph.close()
        ideas = sorted(ideas, key=lambda k: int(k["index"]))
        for idea in ideas:
            idea = Idea(idea["id"])
            yield idea

    def data(self):
        content = {
            "id": self.contId,
            "level": self.level,
            "ideas": [i.data() for i in self.ideas]
        }
        return content


class Idea:
    def __init__(self,  ideaId):
        self.ideaId = ideaId
        self.text = None
        self.parents = None
        self.entities = self.getEntities()
        self.lemmas = self.getLemmas()

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        idea = graph.run(
            "MATCH (i:Idea)<--(c:Content) WHERE ID(i)={} RETURN i.text AS text, COLLECT(ID(c)) AS parents".format(self.ideaId)).data()[0]
        graph.close()
        self.text = idea["text"]
        self.parents = idea["parents"]

    def getEntities(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entities = graph.run(
            "MATCH (i:Idea)-[r]->(e:Entity) WHERE ID(i)={} RETURN id(e) AS id, TYPE(r) as index".format(self.ideaId)).data()
        graph.close()
        entities = sorted(entities, key=lambda k: int(k["index"]))
        for entity in entities:
            entity = Entity(entity["id"])
            yield entity

    def getLemmas(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        lemmas = graph.run(
            "MATCH (i:Idea)-[r]->(l:Lemma) WHERE ID(i)={} RETURN id(l) AS id, TYPE(r) as index".format(self.ideaId)).data()
        graph.close()
        lemmas = sorted(lemmas, key=lambda k: int(k["index"]))
        for lemma in lemmas:
            lemma = Lemma(lemma["id"])
            yield lemma

    def data(self):
        idea = {
            "id": self.ideaId,
            "text": self.text,
            "entities": [e.data() for e in self.entities],
            "lemmas": [l.data() for l in self.lemmas]
        }
        return idea

    def relatedIdeas(self):
        relIdeas = []
        relNodes = [e.entId for e in self.entities] + [l.lemId
                                                       for l in self.lemmas]
        relIndex = len(relNodes)
        while relIndex > 2:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            ideas = graph.run(
                "WITH {} as ids MATCH (i:Idea)-->(n) WHERE ID(n) in ids WITH i, {} as allCnt, count(DISTINCT n) as relCnt WHERE relCnt = allCnt RETURN ID(i) AS id, relCnt".format(relNodes, relIndex)).data()
            graph.close()
            ideas = [Idea(i["id"]) for i in ideas if i["id"] != self.ideaId]
            relIdeas = relIdeas + ideas
            relIndex -= 1
        return relIdeas

    def relatedContents(self):
        relContents = []
        relNodes = [e.entId for e in self.entities] + [l.lemId
                                                       for l in self.lemmas]
        relIndex = len(relNodes)
        while relIndex > 2:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            contents = graph.run(
                "WITH {} as ids MATCH (c:Content)-->(i:Idea)-->(n) WHERE ID(n) in ids WITH c, {} as allCnt, count(DISTINCT n) as relCnt WHERE relCnt = allCnt RETURN ID(c) AS id, relCnt".format(relNodes, relIndex)).data()
            graph.close()
            contents = [Content(c["id"])
                        for c in contents if c["id"] not in self.parents]
            relContents = relContents + contents
            relIndex -= 1
        return relContents


class Entity:
    def __init__(self, entId):
        self.entId = entId
        self.name = None
        self.entType = None

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entity = graph.run(
            "MATCH (e:Entity) WHERE ID(e)={} RETURN e.name AS name, e.entType AS entType".format(self.entId)).data()[0]
        graph.close()
        self.name = entity["name"]
        self.pos = entity["entType"]

    def data(self):
        entity = {
            "id": self.entId,
            "name": self.name,
            "entType": self.entType
        }
        return entity


class Lemma:
    def __init__(self, lemId):
        self.lemId = lemId
        self.name = None
        self.pos = None

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        lemma = graph.run(
            "MATCH (l:Lemma) WHERE ID(l)={} RETURN l.name AS name, l.pos AS pos".format(self.lemId)).data()[0]
        graph.close()
        self.name = lemma["name"]
        self.pos = lemma["pos"]

    def data(self):
        lemma = {
            "id": self.lemId,
            "name": self.name,
            "pos": self.pos
        }
        return lemma
