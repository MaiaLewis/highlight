from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
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
    def __init__(self, title, author, lastModified, html):
        self.title = title
        self.author = author
        self.lastModified = lastModified
        self.html = html
        self.contents = []

        self.extractContent()

    def extractContent(self):
        soup = BeautifulSoup(self.html, features="html.parser")
        doc = soup.body
        index = 0
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
                    level = self.findTextSizes().index(textSize)
                    newContent = Content(index, level, text)
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
        return sizes

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
        print(self.title)
        transaction = graph.begin()
        docNode = Node("Document", title=self.title,
                       author=self.author, lastModified=self.lastModified)
        transaction.create(docNode)
        for content in self.contents:
            contNode = Node("Content", level=content.level)
            contRel = Relationship(docNode, str(content.index), contNode)
            transaction.create(contNode)
            transaction.create(contRel)
            for idea in content.ideas:
                ideaNode = Node("Idea", text=idea.text)
                ideaRel = Relationship(contNode, str(idea.index), ideaNode)
                transaction.create(ideaNode)
                transaction.create(ideaRel)
                for lemma in idea.lemmas:
                    lemmaNode = Node("Lemma", name=lemma.name)
                    lemmaRel = Relationship(
                        ideaNode, str(lemma.index), lemmaNode)
                    transaction.create(lemmaNode)
                    transaction.create(lemmaRel)
                for entity in idea.entities:
                    entNode = Node("Entity", name=entity.name)
                    entRel = Relationship(ideaNode, str(entity.index), entNode)
                    transaction.create(entNode)
                    transaction.create(entRel)
        transaction.commit()


class Content:
    def __init__(self, index, level, text):
        self.index = index
        self.text = text
        self.level = level
        self.ideas = []

        self.processContent()

    def processContent(self):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.text)
        index = 0
        for sentence in doc.sents:
            lemmas = []
            entities = []
            for token in sentence:
                if token.pos_ in ["VERB", "NOUN"]:
                    lemmas.append(token.lemma_)
            for entity in sentence.ents:
                entities.append(entity.text)
            newIdea = Idea(index, sentence.text, lemmas, entities)
            self.ideas.append(newIdea)
            index += 1


class Idea:
    def __init__(self,  index, text, lemmas, entities):
        self.index = index
        self.text = text
        self.lemmaText = lemmas
        self.entityText = entities
        self.lemmas = []
        self.entities = []

        self.createLemmas()
        self.createEntities()

    def createLemmas(self):
        index = 0
        for lemma in self.lemmaText:
            newLemma = Lemma(index, lemma)
            self.lemmas.append(newLemma)
            index += 1

    def createEntities(self):
        index = 0
        for entity in self.entityText:
            newEntity = Entity(index, entity)
            self.entities.append(newEntity)
            index += 1


class Lemma:
    def __init__(self, index, name):
        self.index = index
        self.name = name


class Entity:
    def __init__(self, index, name):
        self.index = index
        self.name = name
