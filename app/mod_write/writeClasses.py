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
        self.author = author
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
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        for text in nlp.pipe(self.text, disable=["parser"]):
            newContent = CreateContent(index, self.levels[index], text)
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
        print("starting save")
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        graph.run(
            "CREATE (d:Document {{docId:'{}', title:'{}', author:'{}', lastModified:'{}'}})".format(self.docId, self.title, self.author, self.lastModified))
        graph.close()
        for content in self.contents:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            contentId = graph.run(
                "MATCH (d:Document {{docId:'{}'}}) CREATE (c:Content {{level:'{}'}}) CREATE (d)-[:`{}`]->(c) RETURN ID(c) as id".format(self.docId, content.level, str(content.index))).data()[0]["id"]
            graph.close()
            for idea in content.ideas:
                ideaText = idea.text.replace("'", '\\"')
                graph = driver.session()  # pylint: disable=assignment-from-no-return
                existingIdea = graph.run(
                    "MATCH (i:Idea {{text: '{}'}}) RETURN ID(i) AS id".format(ideaText)).data()
                graph.close()
                if existingIdea:
                    ideaId = existingIdea[0]["id"]
                else:
                    graph = driver.session()  # pylint: disable=assignment-from-no-return
                    ideaId = graph.run(
                        "CREATE (i:Idea {{text: '{}'}}) RETURN ID(i) AS id".format(ideaText)).data()[0]["id"]
                    graph.close()
                graph = driver.session()  # pylint: disable=assignment-from-no-return
                graph.run("MATCH (c:Content) WHERE ID(c)={} MATCH (i:Idea) WHERE ID(i)={} CREATE (c)-[:`{}`]->(i)".format(
                    contentId, ideaId, str(idea.index)))
                graph.close()
                for lemma in idea.lemmas:
                    graph = driver.session()  # pylint: disable=assignment-from-no-return
                    existingLemma = graph.run(
                        "MATCH (l:Lemma {{name: '{}', pos: '{}'}}) RETURN ID(l) AS id".format(lemma.name, lemma.pos)).data()
                    graph.close()
                    if existingLemma:
                        lemmaId = existingLemma[0]["id"]
                    else:
                        graph = driver.session()  # pylint: disable=assignment-from-no-return
                        lemmaId = graph.run(
                            "CREATE (l:Lemma {{name: '{}', pos: '{}'}}) RETURN ID(l) AS id".format(lemma.name, lemma.pos)).data()[0]["id"]
                        graph.close()
                    graph = driver.session()  # pylint: disable=assignment-from-no-return
                    graph.run("MATCH (i:Idea) WHERE ID(i)={} MATCH (l:Lemma) WHERE ID(l)={} CREATE (i)-[:`{}`]->(l)".format(
                        ideaId, lemmaId, str(lemma.index)))
                    graph.close()
                for entity in idea.entities:
                    graph = driver.session()  # pylint: disable=assignment-from-no-return
                    existingEntity = graph.run(
                        "MATCH (e:Entity {{name: '{}'}}) RETURN ID(e) AS id".format(entity.name)).data()
                    graph.close()
                    if existingEntity:
                        entityId = existingEntity[0]["id"]
                    else:
                        graph = driver.session()  # pylint: disable=assignment-from-no-return
                        entityId = graph.run(
                            "CREATE (e:Entity {{name: '{}', entType: '{}'}}) RETURN ID(e) AS id".format(entity.name, entity.entType)).data()[0]["id"]
                        graph.close()
                    graph = driver.session()  # pylint: disable=assignment-from-no-return
                    graph.run("MATCH (i:Idea) WHERE ID(i)={} MATCH (e:Entity) WHERE ID(e)={} CREATE (i)-[:`{}`]->(e)".format(
                        ideaId, entityId, str(entity.index)))
                    graph.close()
        topics = self.findTopics()
        for topic in topics:
            graph = driver.session()  # pylint: disable=assignment-from-no-return
            graph.run(
                "MATCH (d:Document {{docId:'{}'}}) MATCH (n) WHERE ID(n)={} CREATE (d)-[:Topic {{degree: '{}'}}]->(n)".format(self.docId, topic["id"], topic["degree"]))
            graph.close()
        print("save finished")

    def findTopics(self):
        topics = []
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        entTopics = graph.run(
            "MATCH (n:Document {{docId:'{}'}})-->(c:Content)-->(i:Idea)-->(e:Entity) RETURN ID(e) as id,  SIZE(COLLECT(i)) as cnt ORDER BY cnt DESC LIMIT 10".format(self.docId)).data()
        graph.close()
        for e in entTopics:
            if e["cnt"] > 1:
                topics.append({"id": e["id"], "degree": e["cnt"]})
        graph = driver.session()  # pylint: disable=assignment-from-no-return
        lemTopics = graph.run(
            "MATCH (n:Document {{docId:'{}'}})-->(c:Content)-->(i:Idea)-->(l:Lemma {{pos:'NOUN'}}) WHERE NOT l.name IN ['thing', 'something', 'someone', 'way', 'lot', 'minute', 'hour', 'day', 'week', 'year', 'today', 'tomorrow', 'time', 'reason', 'point', 'detail'] RETURN ID(l) as id,  SIZE(COLLECT(i)) as cnt ORDER BY cnt DESC LIMIT 10".format(self.docId)).data()
        graph.close()
        for l in lemTopics:
            if l["cnt"] > 2:
                topics.append({"id": l["id"], "degree": l["cnt"]})
        return topics


class CreateContent:
    def __init__(self, index, level, nlpObject):
        self.index = index
        self.nlpObject = nlpObject
        self.level = level
        self.ideas = []

        self.processContent()

    def processContent(self):
        index = 0
        for sentence in self.nlpObject.sents:
            newIdea = CreateIdea(index, sentence)
            self.ideas.append(newIdea)
            index += 1


class CreateIdea:
    def __init__(self,  index, nlpObject):
        self.index = index
        self.nlpObject = nlpObject
        self.text = nlpObject.text
        self.lemmas = []
        self.entities = []

        self.processIdea()

    def processIdea(self):
        index = 0
        for token in self.nlpObject:
            if token.pos_ in ["VERB", "NOUN"] and token.lemma_ not in ["be", "have", "can", "do"]:
                newLemma = CreateLemma(index, token.lemma_, token.pos_)
                self.lemmas.append(newLemma)
                index += 1
        index = 0
        for entity in self.nlpObject.ents:
            if entity.label_ not in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]:
                newEntity = CreateEntity(index, entity.text, entity.label_)
                self.entities.append(newEntity)
                index += 1


class CreateLemma:
    def __init__(self, index, name, pos):
        self.index = index
        self.name = name
        self.pos = pos


class CreateEntity:
    def __init__(self, index, name, entType):
        self.index = index
        self.name = name
        self.entType = entType
