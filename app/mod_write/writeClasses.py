from neo4j.v1 import GraphDatabase, basic_auth
import spacy
from bs4 import BeautifulSoup
import re
import os

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


class CreateDocument:
    def __init__(self, docId, title, author, lastModified, html):
        self.docId = docId
        self.title = title
        self.author = CreateAuthor(author)
        self.lastModified = lastModified
        self.html = html
        self.textSizes = []
        self.text = []
        self.levels = []
        self.contents = []

        self.findTextSizes()
        self.extractContent()
        self.processContent()

    def extractContent(self):
        print(self.title)
        soup = BeautifulSoup(self.html, features="html.parser")
        doc = soup.body
        for tag in doc.children:
            if tag.name.startswith("h") or tag.name == "p":
                text = ""
                for string in tag.stripped_strings:
                    text = text + string + " "
                text = str(text)
                if len(text) > 0:
                    firstString = list(tag.strings)[0]
                    sizeParent = self.findSizeParent(firstString.parent)
                    textSize = self.findTextSize(sizeParent)
                    level = self.textSizes.index(textSize)
                    self.text.append(text)
                    self.levels.append(level)

    def processContent(self):
        index = 0
        nlp = spacy.load("en_core_web_sm")
        for text in nlp.pipe(self.text, disable=["ner"]):
            newContent = CreateContent(self.levels[index], text)
            self.contents.append(newContent)
            index += 1

    def findTextSizes(self):
        doc = BeautifulSoup(self.html, features="html.parser")
        tags = doc.find_all(style=True)
        sizes = []
        for tag in tags:
            size = self.findTextSize(tag)
            if size not in sizes and size != 0:
                sizes.append(size)
        sizes.sort()
        self.textSizes = sizes

    def findSizeParent(self, tag):
        if "style" in tag.attrs and self.findTextSize(tag) != 0:
            return tag
        else:
            return self.findSizeParent(tag.parent)

    def findTextSize(self, tag):
        styleAttribute = tag["style"]
        size = re.findall(r"font-size:(\d+)pt", styleAttribute)
        if len(size) > 0:
            size = size[0]
            return int(size)
        return 0

    def save(self):
        authorId = self.author.save()
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        graph.run(
            "MATCH (a:Author) WHERE ID(a)={} CREATE (d:Document {{docId:'{}', title:'{}', lastModified:'{}'}})<-[:Owner]-(a)".format(authorId, self.docId, self.title, self.lastModified))
        graph.close()
        for content in self.contents:
            contentId = content.save()
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            graph.run("MATCH (d:Document {{docId:'{}'}}) MATCH (c:Content) WHERE ID(c)={} CREATE (d)-[:Includes {{index: {}}}]->(c)".format(
                self.docId, contentId, self.contents.index(content)))
            graph.close()
        topics = self.findTopics()
        for topic in topics:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            graph.run(
                "MATCH (d:Document {{docId:'{}'}}) MATCH (n) WHERE ID(n)={} CREATE (d)-[:Topic {{frequency: '{}'}}]->(n)".format(self.docId, topic["id"], topic["frequency"]))
            graph.close()

    def findTopics(self):
        topics = []
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entTopics = graph.run(
            "MATCH (n:Document {{docId:'{}'}})-->(c:Content)-->(i:Idea)-->(e:Entity) WHERE NOT e.name in ['thing', 'something', 'someone', 'way', 'lot', 'minute', 'hour', 'day', 'week', 'year', 'today', 'tomorrow', 'time', 'reason', 'point', 'detail'] RETURN ID(e) as id,  SIZE(COLLECT(i)) as frq ORDER BY frq DESC LIMIT 10".format(self.docId)).data()
        graph.close()
        for e in entTopics:
            if e["frq"] > 2:
                topics.append({"id": e["id"], "frequency": e["frq"]})
        return topics


class CreateAuthor:
    def __init__(self, name):
        self.name = name

    def save(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        authorId = graph.run(
            "MERGE (a:Author {{name:'{}'}}) RETURN ID(a) AS id".format(self.name)).data()[0]["id"]
        graph.close()
        return authorId


class CreateContent:
    def __init__(self, level, nlpObject):
        self.nlpObject = nlpObject
        self.level = level
        self.ideas = []

        self.processContent()

    def processContent(self):
        for sentence in self.nlpObject.sents:
            newIdea = CreateIdea(sentence)
            self.ideas.append(newIdea)

    def save(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        contentId = graph.run(
            "CREATE (c:Content {{level:'{}'}}) RETURN ID(c) AS id".format(self.level)).data()[0]["id"]
        graph.close()
        for idea in self.ideas:
            ideaId = idea.save()
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            graph.run("MATCH (c:Content) WHERE ID(c)={} MATCH (i:Idea) WHERE ID(i)={} CREATE (c)-[:Includes {{index: {}}}]->(i)".format(
                contentId, ideaId, self.ideas.index(idea)))
            graph.close()
        return contentId


class CreateIdea:
    def __init__(self,  nlpObject):
        self.nlpObject = nlpObject
        self.text = nlpObject.text
        self.entities = []

        self.processIdea()

    def processIdea(self):
        print(self.text)
        for chunk in self.nlpObject.noun_chunks:
            tokens = []
            for token in chunk:
                if token.pos_ in ["NOUN", "PROPN"] and token.text not in ['’s', '“', '”', '\"', '_', "’"]:
                    tokens.append(token)
                    print(token.text)
            if tokens:
                newEntity = CreateEntity(tokens)
                self.entities.append(newEntity)

    def save(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        ideaText = self.text.replace("'", '\\"')
        ideaId = graph.run(
            "MERGE (i:Idea {{text: '{}'}}) RETURN ID(i) AS id".format(ideaText)).data()[0]["id"]
        graph.close()
        for entity in self.entities:
            entityId = entity.save()
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            graph.run("MATCH (i:Idea) WHERE ID(i)={} MATCH (e:Entity) WHERE ID(e)={} MERGE (i)-[:Includes {{index: {}}}]->(e)".format(
                ideaId, entityId, self.entities.index(entity)))
            graph.close()
        return ideaId


class CreateEntity:
    def __init__(self, nlpObjects):
        self.nlpObjects = nlpObjects
        self.name = ""
        self.entType = "basic"

        self.processEntity()

    def processEntity(self):
        if len(self.nlpObjects) > 1:
            self.entType = "named"
        for token in self.nlpObjects:
            if token.pos_ == "PROPN":
                self.entType = "named"
            self.name = self.name + token.lemma_.lower() + " "
        self.name = self.name[:-1]

    def save(self):
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entityId = graph.run(
            "MERGE (e:Entity {{name: '{}', entType: '{}'}}) RETURN ID(e) AS id".format(self.name, self.entType)).data()[0]["id"]
        graph.close()
        return entityId
