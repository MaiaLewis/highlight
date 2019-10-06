from neo4j.v1 import GraphDatabase, basic_auth
import json
import os

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


class Graph:
    def __init__(self, topicFilters=[], authorFilters=[], documentFilters=[]):
        self.topicFilters = [Entity(t) for t in topicFilters]
        self.authorFilters = [Author(a) for a in authorFilters]
        self.documentFilters = documentFilters
        self.documents = self.getDocuments()

    def getDocuments(self):
        # TODO Can this logic be built into one query
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        isFiltered = False
        if self.topicFilters:
            topDocs = graph.run(
                "WITH {} as topIds MATCH (d:Document)-->(c:Content)-->(i:Idea)-->(n) WHERE ID(n) in topIds WITH d, SIZE(topIds) as allCnt, count(DISTINCT n) as relCnt WHERE relCnt = allCnt RETURN d.docId AS id".format([t.id for t in self.topicFilters])).data()
            filteredDocs = [d["id"] for d in topDocs]
            isFiltered = True
        if self.authorFilters:
            authDocs = graph.run(
                "WITH {} as ids MATCH (d:Document)<--(a:Author) WHERE ID(a) in ids RETURN d.docId AS id".format([a.id for a in self.authorFilters])).data()
            if not isFiltered:
                filteredDocs = [d["id"] for d in authDocs]
                isFiltered = True
            else:
                filteredDocs = list(
                    set(filteredDocs).intersection(set([d["id"] for d in authDocs])))
        if self.documentFilters:
            if not isFiltered:
                filteredDocs = self.documentFilters
                isFiltered = True
            else:
                filteredDocs = list(
                    set(filteredDocs).intersection(set(self.documentFilters)))
        if isFiltered:
            documents = graph.run(
                "WITH {} as docIds MATCH (d:Document) WHERE d.docId in docIds RETURN d.docId as docId, d.lastModified as lastModified ORDER BY lastModified DESC LIMIT 50".format(filteredDocs)).data()
        else:
            documents = graph.run(
                "MATCH (d:Document) RETURN d.docId as docId, d.lastModified as lastModified ORDER BY lastModified DESC LIMIT 50").data()
        graph.close()
        for document in documents:
            document = Document(document["docId"], self.topicFilters)
            yield document

    def data(self):
        documents = self.getDocuments()
        graph = {
            "topicFilters": [t.data() for t in self.topicFilters],
            "authorFilters": [a.data() for a in self.authorFilters],
            "documentFilters": self.documentFilters,
            "documents": []
        }
        for document in documents:
            document = {
                "title": document.title,
                "topics": [t.data() for t in document.topics][:5],
                "snippet": [s.data() for s in document.snippet],
                "author": document.author.data(),
                "lastModified": document.lastModified,
                "docId": document.docId,
            }
            graph["documents"].append(document)
        return graph

    def trendingTopics(self):
        # TODO There must be a shorter way to write this
        documents = self.getDocuments()
        recentDocs = [d.docId for d in documents]
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        allMentions = graph.run(
            "MATCH (d:Document)-->(c:Content)-->(i:Idea)-->(e:Entity) RETURN ID(e) AS topic, COLLECT(DISTINCT d.docId) as docs, SIZE(COLLECT(d)) AS frq ORDER BY frq DESC LIMIT 50").data()
        recentMentions = graph.run(
            "WITH {} as docIds MATCH (d:Document)-->(c:Content)-->(i:Idea)-->(e:Entity) WHERE d.docId IN docIds RETURN ID(e) AS topic, COLLECT(DISTINCT d.docId) as docs, SIZE(COLLECT(d)) AS frq ORDER BY frq DESC LIMIT 20".format(recentDocs)).data()
        recentTopics = graph.run(
            "WITH {} as docIds MATCH (d:Document)-[:Topic]->(e:Entity) WHERE d.docId IN docIds RETURN ID(e) AS topic, COLLECT(DISTINCT d.docId) as docs, SIZE(COLLECT(d)) AS frq ORDER BY frq DESC LIMIT 50".format(recentDocs)).data()
        graph.close()
        allMentionList = [t["topic"] for t in allMentions]
        recentMentionList = [t["topic"] for t in recentMentions]
        recentTopicList = [t["topic"] for t in recentTopics]
        trendingTopics = []
        duplicateTopics = []
        for topic in recentMentionList:
            if topic in recentTopicList:
                if topic not in allMentionList or recentMentionList.index(topic) - allMentionList.index(topic) <= -2:
                    trendingTopics.append(
                        recentMentions[recentMentionList.index(topic)])
        for topic in trendingTopics:
            for possibleDup in trendingTopics[::-1]:
                if trendingTopics.index(possibleDup) > trendingTopics.index(topic):
                    if len(set(topic["docs"]).intersection(set(possibleDup["docs"])))/len(topic["docs"]) > .5:
                        duplicateTopics.append(possibleDup)
                        break
        duplicateTopics = [t["topic"] for t in duplicateTopics]
        trendingTopicGraphs = []
        for topic in trendingTopics:
            if topic["topic"] not in duplicateTopics:
                trendingTopicGraphs.append(
                    Graph(topicFilters=[topic["topic"]], documentFilters=recentDocs))
        return trendingTopicGraphs

    def trendingAuthors(self):
        if not self.documents:
            self.getDocuments()
        recentDocs = [d.docId for d in self.documents]
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        recentAuthors = graph.run(
            "WITH {} as docIds MATCH (d:Document)<--(a:Author) WHERE d.docId IN docIds RETURN ID(a) AS author, SIZE(COLLECT(d)) AS frq ORDER BY frq DESC LIMIT 10".format(recentDocs)).data()
        trendingAuthorGraphs = []
        for author in recentAuthors:
            trendingAuthorGraphs.append(
                Graph(authorFilters=[author["author"]], documentFilters=recentDocs))
        return trendingAuthorGraphs


class Document:
    def __init__(self, docId, topicFilters=[]):
        self.docId = docId
        self.title = None
        self.author = None
        self.lastModified = None
        self.topicFilters = topicFilters
        self.topics = None
        self.snippet = None
        self.contents = self.getContents()

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        document = graph.run(
            "MATCH (d:Document {{docId:'{}'}})<-[:Owner]-(a:Author) RETURN d.title AS title, ID(a) AS author, d.lastModified AS lastModified".format(self.docId)).data()[0]
        graph.close()
        self.title = document["title"]
        self.author = Author(document["author"])
        self.lastModified = document["lastModified"]
        self.getTopics()
        self.getSnippet()

    def getContents(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        contents = graph.run(
            "MATCH (d:Document {{docId:'{}'}})-[r]->(c:Content) RETURN id(c) AS id, r.index as index".format(self.docId)).data()
        graph.close()
        contents = sorted(contents, key=lambda k: k["index"])
        for content in contents:
            content = Content(content["id"])
            yield content

    def getSnippet(self):
        ideas = []
        if self.topicFilters:
            relIndex = len(self.topicFilters)
            while relIndex > 0 and not ideas:
                graph = driver.session()  # pylint: disable=assignment-from-no-return
                ideas = graph.run("WITH {} as ids MATCH (d:Document {{docId: '{}'}})-->(c:Content)-->(i:Idea)-->(n) WHERE ID(n) in ids WITH i, {} as allCnt, count(DISTINCT n) as relCnt WHERE relCnt = allCnt RETURN ID(i) AS id, relCnt".format(
                    [t.id for t in self.topicFilters], self.docId, relIndex)).data()
                graph.close()
                relIndex -= 1
        elif self.topics:
            topics = [t.id for t in self.topics]
            relIndex = len(topics)
            while relIndex > 0 and not ideas:
                graph = driver.session()  # pylint: disable=assignment-from-no-return
                ideas = graph.run("WITH {} as ids MATCH (d:Document {{docId: '{}'}})-->(c:Content)-->(i:Idea)-->(n) WHERE ID(n) in ids WITH i, {} as allCnt, count(DISTINCT n) as relCnt WHERE relCnt = allCnt RETURN ID(i) AS id, relCnt".format(
                    topics, self.docId, relIndex)).data()
                graph.close()
                relIndex -= 1
        else:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            ideas = graph.run("MATCH (d:Document {{docId: '{}'}})-[:Includes {{index: 0}}]->(c:Content)-[:Includes {{index: 0}}]->(i:Idea) RETURN ID(i) AS id".format(
                self.docId)).data()
            graph.close()
        snippet = [Idea(i["id"]) for i in ideas]
        self.snippet = snippet

    def getTopics(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        namedTopics = []
        basicTopics = []
        topics = graph.run(
            "MATCH (d:Document {{docId:'{}'}})-[t:Topic]->(n) RETURN n.entType as entType, ID(n) AS id, t.frequency AS frequency".format(self.docId)).data()
        graph.close()
        topics = sorted(topics, key=lambda k: int(
            k["frequency"]), reverse=True)
        for topic in topics:
            if topic["entType"] == "named":
                topic = Entity(topic["id"], topic["frequency"])
                namedTopics.append(topic)
            elif topic["entType"] == "basic":
                topic = Entity(topic["id"], topic["frequency"])
                basicTopics.append(topic)
        topics = namedTopics + basicTopics
        self.topics = topics

    def data(self):
        contents = self.getContents()
        document = {
            "id": self.docId,
            "title": self.title,
            "author": self.author.data(),
            "lastModified": self.lastModified,
            "contents": [c.data() for c in contents],
            "topics": [t.data() for t in self.topics],
            "snippet": [s.data() for s in self.snippet]
        }
        return document


class Author:
    def __init__(self, id):
        self.id = id
        self.name = None

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        author = graph.run(
            "MATCH (a:Author) WHERE ID(a)={} RETURN a.name AS name".format(self.id)).data()[0]
        graph.close()
        self.name = author["name"]

    def data(self):
        author = {
            "id": self.id,
            "name": self.name
        }
        return author


class Content:
    def __init__(self, id):
        self.id = id
        self.level = None
        self.parents = None
        self.ideas = self.getIdeas()

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        content = graph.run(
            "MATCH (c:Content)<--(d:Document) WHERE ID(c)={} RETURN c.level AS level, COLLECT(d.docId) AS parents".format(self.id)).data()[0]
        graph.close()
        self.level = content["level"]
        self.parents = content["parents"]

    def getIdeas(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        ideas = graph.run(
            "MATCH (c:Content)-[r]->(i:Idea) WHERE ID(c)={} RETURN id(i) AS id, r.index AS index".format(self.id)).data()
        graph.close()
        ideas = sorted(ideas, key=lambda k: k["index"])
        for idea in ideas:
            idea = Idea(idea["id"])
            yield idea

    def data(self):
        ideas = self.getIdeas()
        content = {
            "id": self.id,
            "level": self.level,
            "ideas": [i.data() for i in ideas]
        }
        return content


class Idea:
    def __init__(self, id):
        self.id = id
        self.text = None
        self.parents = None
        self.entities = self.getEntities()

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        idea = graph.run(
            "MATCH (i:Idea)<--(c:Content) WHERE ID(i)={} RETURN i.text AS text, COLLECT(ID(c)) AS parents".format(self.id)).data()[0]
        graph.close()
        self.text = idea["text"]
        self.parents = idea["parents"]

    def getEntities(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entities = graph.run(
            "MATCH (i:Idea)-[r]->(e:Entity) WHERE ID(i)={} RETURN id(e) AS id, r.index as index".format(self.id)).data()
        graph.close()
        entities = sorted(entities, key=lambda k: k["index"])
        for entity in entities:
            entity = Entity(entity["id"])
            yield entity

    def data(self):
        entities = self.getEntities()
        idea = {
            "id": self.id,
            "text": self.text,
            "entities": [e.data() for e in entities],
        }
        return idea

    def relatedIdeas(self):
        entities = self.getEntities()
        relIdeas = []
        relNodes = [e.id for e in entities]
        relIndex = len(relNodes)
        while relIndex > 2:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            ideas = graph.run(
                "WITH {} as ids MATCH (i:Idea)-->(n) WHERE ID(n) in ids WITH i, {} as allCnt, count(DISTINCT n) as relCnt WHERE relCnt = allCnt RETURN ID(i) AS id, relCnt".format(relNodes, relIndex)).data()
            graph.close()
            ideas = [Idea(i["id"]) for i in ideas if i["id"] != self.id]
            relIdeas = relIdeas + ideas
            relIndex -= 1
        return relIdeas

    def relatedContents(self):
        entities = self.getEntities()
        relContents = []
        relNodes = [e.id for e in entities]
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
    def __init__(self, id, frequency=None):
        self.id = id
        self.frequency = frequency
        self.name = None
        self.entType = None

        self.build()

    def build(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entity = graph.run(
            "MATCH (e:Entity) WHERE ID(e)={} RETURN e.name AS name, e.entType AS entType".format(self.id)).data()[0]
        graph.close()
        self.name = entity["name"]
        self.entType = entity["entType"]

    def data(self):
        entity = {
            "id": self.id,
            "name": self.name,
            "entType": self.entType,
            "frequency": self.frequency
        }
        return entity
