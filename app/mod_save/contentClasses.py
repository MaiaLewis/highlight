from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship, NodeMatcher
import spacy
from bs4 import BeautifulSoup
import re
import os

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

graph = Graph(graphenedb_url, user=graphenedb_user, password=graphenedb_pass,
              bolt=True, secure=True, http_port=24789, https_port=24780)


class Document:
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
            newContent = Content(index, self.levels[index], text)
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
        transaction = graph.begin()
        matcher = NodeMatcher(graph)
        docNode = Node("Document", docId=self.docId, title=self.title,
                       author=self.author, lastModified=self.lastModified)
        transaction.create(docNode)
        transaction.commit()
        for content in self.contents:
            transaction = graph.begin()
            contNode = Node("Content", level=content.level)
            contRel = Relationship(docNode, str(content.index), contNode)
            transaction.create(contNode)
            transaction.create(contRel)
            transaction.commit()
            for idea in content.ideas:
                transaction = graph.begin()
                ideaText = idea.text.replace('"', '\\"')
                ideaNode = matcher.match("Idea").where(
                    '_.text = "{}"'.format(ideaText)).first()
                if not ideaNode:
                    ideaNode = Node("Idea", text=ideaText)
                    transaction.create(ideaNode)
                ideaRel = Relationship(contNode, str(idea.index), ideaNode)
                transaction.create(ideaRel)
                transaction.commit()
                for lemma in idea.lemmas:
                    transaction = graph.begin()
                    lemmaNode = matcher.match("Lemma").where(
                        '_.name = "{}"'.format(lemma.name)).first()
                    print(lemmaNode)
                    if not lemmaNode:
                        lemmaNode = Node(
                            "Lemma", name=lemma.name, pos=lemma.pos)
                        transaction.create(lemmaNode)
                    lemmaRel = Relationship(
                        ideaNode, str(lemma.index), lemmaNode)
                    transaction.create(lemmaRel)
                    transaction.commit()
                for entity in idea.entities:
                    transaction = graph.begin()
                    entNode = matcher.match("Entity").where(
                        '_.name = "{}"'.format(entity.name)).first()
                    if not entNode:
                        entNode = Node("Entity", name=entity.name,
                                       entType=entity.entType)
                        transaction.create(entNode)
                    entRel = Relationship(
                        ideaNode, str(entity.index), entNode)
                    transaction.create(entRel)
                    transaction.commit()
        print("save finished")


class Content:
    def __init__(self, index, level, nlpObject):
        self.index = index
        self.nlpObject = nlpObject
        self.level = level
        self.ideas = []

        self.processContent()

    def processContent(self):
        index = 0
        for sentence in self.nlpObject.sents:
            newIdea = Idea(index, sentence)
            self.ideas.append(newIdea)
            index += 1


class Idea:
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
                newLemma = Lemma(index, token.lemma_, token.pos_)
                self.lemmas.append(newLemma)
                index += 1
        index = 0
        for entity in self.nlpObject.ents:
            if entity.label_ not in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]:
                newEntity = Entity(index, entity.text, entity.label_)
                self.entities.append(newEntity)
                index += 1


class Lemma:
    def __init__(self, index, name, pos):
        self.index = index
        self.name = name
        self.pos = pos


class Entity:
    def __init__(self, index, name, entType):
        self.index = index
        self.name = name
        self.entType = entType
