import flask
from flask_cors import CORS
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from neo4j.v1 import GraphDatabase, basic_auth
import json
import random
import string

app = flask.Flask(__name__, static_folder="build/static",
                  template_folder="build")
app.secret_key = "secret"
CORS(app)

graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

driver = GraphDatabase.driver(
    graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))


@app.route('/')
def index():
    return flask.render_template("index.html")


@app.route('/search')
def search():
    if 'credentials' not in flask.session:
        # redirect to authorize user
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        # connect to Drive API
        credentials = Credentials(**flask.session['credentials'])
        drive = build('drive', 'v3', credentials=credentials)
        results = drive.files().list(  # pylint: disable=no-member
            pageSize=10, fields="nextPageToken, files(id, name, owners(displayName), modifiedTime)").execute()
        # save documents to Graph
        items = results.get('files', [])
        session = driver.session()
        query = ""
        index = 0
        for item in items:
            variable = str(index)
            node = "CREATE ({}:Document {{title: '{}', author: '{}', last_edit: '{}'}}) ".format(
                variable, item["name"], item["owners"][0]["displayName"], item["modifiedTime"])
            print(node)
            query = query + node
            index += 1
        session.run(query)
        # query graph for documents
        items = session.run(
            "MATCH (n:Document) RETURN n.title AS title, n.author AS author, n.last_edit AS last_edit")
        print(items)
        documents = []
        for item in items:
            document = {
                "id": item["id"],
                "title": item["name"],
                "topics": ["Topic 1", "Topic 2", "Topic 3"],
                "author": item["owners"][0]["displayName"],
                "last_edit": item["modifiedTime"]
            }
            documents.append(document)
    session.close()
    documents = json.dumps(documents)
    return documents


@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        flask.session['state'] = state
        url = {"url": authorization_url}
        url = json.dumps(url)
        return url
    else:
        auth_code = flask.request.url
        flow.fetch_token(authorization_response=auth_code)
        credentials = flow.credentials
        flask.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
        return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    app.run()
