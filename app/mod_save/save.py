import flask
from celery import Celery
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
from .createClasses import CreateDocument
import json
import os


mod_save = flask.Blueprint('save', __name__, url_prefix='/save')
celery = Celery('save', broker=os.environ.get('REDIS_URL'),
                backend=os.environ.get('REDIS_URL'))

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

graph = Graph(graphenedb_url, user=graphenedb_user, password=graphenedb_pass,
              bolt=True, secure=True, http_port=24789, https_port=24780)


@mod_save.route('/save')
def save():
    task = saveDocs.delay(flask.session['credentials'])
    progressURL = flask.url_for('save.saveProgress', task_id=task.id)
    print(progressURL)
    flask.session['saveStatus'] = 'saving'
    flask.session['progressURL'] = progressURL
    return json.dumps({'success': True, 'progressURL': progressURL}), 202, {'ContentType': 'application/json'}


@celery.task(bind=True)
def saveDocs(self, sessionCredentials):
    # do I actually need this if statement anymore?
    if not sessionCredentials:
        return flask.redirect(flask.url_for('auth.oauth2callback'))
    else:
        credentials = Credentials(**sessionCredentials)
        drive = build('drive', 'v3', credentials=credentials)
        results = drive.files().list(  # pylint: disable=no-member
            q="mimeType='application/vnd.google-apps.document'", pageSize=100, fields="nextPageToken, files(id, name, owners(displayName), modifiedTime)").execute()
        items = results.get('files', [])
        totalDocs = len(items)
        docIndex = 0
        for item in items:
            html = drive.files().export(  # pylint: disable=no-member
                fileId=item["id"], mimeType="text/html").execute()
            doc = CreateDocument(item["id"], item["name"], item["owners"][0]
                                 ["displayName"], item["modifiedTime"], html)
            try:
                doc.save()
                progressData = {
                    'current': docIndex,
                    'total': totalDocs,
                    'title': doc.title
                }
                self.update_state(state='PROGRESS', meta=progressData)
                docIndex += 1
            except:
                print("save failed")
    return {'current': docIndex, 'total': totalDocs}


@mod_save.route('/progress/<taskId>')
def saveProgress(taskId):
    print(taskId)
    task = saveDocs.AsyncResult(taskId)
    print(task.state)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'currentDocs': 0,
            'totalDocs': 1,
            'status': ''
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'currentDocs': task.info.get('current', 0),
            'totalDocs': task.info.get('total', 1),
            'status': task.info.get('title', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'currentDocs': task.info.get('current', 1),
            'totalDocs': task.info.get('total', 1),
            'status': ''
        }
        flask.session['saveStatus'] = 'up_to_date'
    else:
        response = {
            'state': task.state,
            'currentDocs': 0,
            'totalDocs': 0,
            'status': str(task.info),
        }
    return json.dumps(response)


@mod_save.route('/clear')
def clear():
    graph.run("MATCH (n) DETACH DELETE n")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
