import flask
from celery import Celery
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from neo4j.v1 import GraphDatabase, basic_auth
from .writeClasses import CreateDocument
import json
import os


mod_write = flask.Blueprint('write', __name__, url_prefix='/write')
celery = Celery('write', broker=os.environ.get('REDIS_URL'),
                backend=os.environ.get('REDIS_URL'))

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))

# TODO Rewrite these routes to move DB interactions to writeClasses.py


@mod_write.route('/graph')
def writeGraph():
    task = writeDocuments.delay(flask.session['credentials'])
    progressURL = flask.url_for('write.checkProgress', taskId=task.id)
    flask.session['saveStatus'] = 'saving'
    flask.session['progressURL'] = progressURL
    return json.dumps({'success': True, 'progressURL': progressURL}), 202, {'ContentType': 'application/json'}


@celery.task(bind=True)
def writeDocuments(self, sessionCredentials):
    # TODO do I actually need this if statement anymore?
    if not sessionCredentials:
        return flask.redirect(flask.url_for('auth.oauth2callback'))
    else:
        credentials = Credentials(**sessionCredentials)
        drive = build('drive', 'v3', credentials=credentials)
        results = drive.files().list(  # pylint: disable=no-member
            q="mimeType='application/vnd.google-apps.document'", pageSize=10, fields="nextPageToken, files(id, name, owners(displayName), modifiedTime)").execute()
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


@mod_write.route('/progress/<taskId>')
def checkProgress(taskId):
    print(taskId)
    task = writeDocuments.AsyncResult(taskId)
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


@mod_write.route('/clear')
def clear():
    graph = driver.session()  # pylint: disable=assignment-from-no-return
    graph.run("MATCH (n) DETACH DELETE n")
    graph.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
