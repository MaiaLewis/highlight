import flask
from celery import Celery
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
from .contentClasses import Document
import json
import os


mod_save = flask.Blueprint('save', __name__, url_prefix='/save')
celery = Celery('save', backend=os.environ.get('CELERY_BROKER_URL'),
                broker=os.environ.get('CELERY_BROKER_URL'))

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

graph = Graph(graphenedb_url, user=graphenedb_user, password=graphenedb_pass,
              bolt=True, secure=True, http_port=24789, https_port=24780)


@mod_save.route('/save')
def save():
    credentials = flask.session['credentials']
    saveDocs.delay(credentials)
    flask.session['docsSaved'] = True
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@mod_save.route('/clear')
def clear():
    graph.run("MATCH (n) DETACH DELETE n")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@celery.task()
def saveDocs(sessionCredentials):
    # do I actually need this if statement anymore?
    if not sessionCredentials:
        return flask.redirect(flask.url_for('auth.oauth2callback'))
    else:
        credentials = Credentials(**sessionCredentials)
        drive = build('drive', 'v3', credentials=credentials)
        results = drive.files().list(  # pylint: disable=no-member
            q="mimeType='application/vnd.google-apps.document'", pageSize=10, fields="nextPageToken, files(id, name, owners(displayName), modifiedTime)").execute()
        items = results.get('files', [])
        for item in items:
            html = drive.files().export(  # pylint: disable=no-member
                fileId=item["id"], mimeType="text/html").execute()
            doc = Document(item["name"], item["owners"][0]
                           ["displayName"], item["modifiedTime"], html)
            try:
                doc.save()
            except:
                print("save failed")
