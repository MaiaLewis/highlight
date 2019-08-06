import flask
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from neo4j.v1 import GraphDatabase, basic_auth
import json
import string

mod_save = flask.Blueprint('save', __name__, url_prefix='/save')

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


@mod_save.route('/save')
def search():
    if 'credentials' not in flask.session:
        # redirect to authorize user
        return flask.redirect(flask.url_for('auth.oauth2callback'))
    else:
        # connect to Drive API
        credentials = Credentials(**flask.session['credentials'])
        drive = build('drive', 'v3', credentials=credentials)
        results = drive.files().list(  # pylint: disable=no-member
            pageSize=10, fields="nextPageToken, files(id, name, owners(displayName), modifiedTime)").execute()
        # save documents to Graph
        items = results.get('files', [])
        session = driver.session()  # pylint: disable=assignment-from-no-return
        for item in items:
            node = "CREATE (n:Document {{title: '{}', author: '{}', last_edit: '{}'}}) ".format(
                item["name"], item["owners"][0]["displayName"], item["modifiedTime"])
            session.run(node)
    session.close()
    success = {"documentCount": len(items)}
    return success
