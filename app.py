import flask
from flask_cors import CORS
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json

app = flask.Flask(__name__, static_folder="build/static",
                  template_folder="build")
CORS(app)


@app.route('/')
def index():
    return flask.render_template("index.html")


@app.route('/search')
def search():
    dummy_results = [
        {
            "id": 1,
            "title": "Document Title",
            "topics": ["Topic 1", "Topic 2", "Topic 3"],
            "author": "Author Name",
            "last_edit": "yyyy-mm-ddThh:mm:ss.ffffff"
        },
        {
            "id": 2,
            "title": "Document Title",
            "topics": ["Topic 1", "Topic 2", "Topic 3"],
            "author": "Author Name",
            "last_edit": "yyyy-mm-ddThh:mm:ss.ffffff"
        },
        {
            "id": 3,
            "title": "Document Title",
            "topics": ["Topic 1", "Topic 2", "Topic 3"],
            "author": "Author Name",
            "last_edit": "yyyy-mm-ddThh:mm:ss.ffffff"
        }]
    credentials = flask.session.get('credentials')
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))
    elif credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        print('now calling fetch')
        # Call the Drive v3 API
        service = build('drive', 'v3', credentials=credentials)
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(item)
    dummy_results = json.dumps(dummy_results)
    return dummy_results


@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
        redirect_uri=flask.url_for('oauth2callback', _external=True))  # access drive api using developer credentials
    if 'code' not in flask.request.args:
        authorization_url, state = flow.authorization_url(
            include_granted_scopes='true')
        print("url")
        print(authorization_url)
        return flask.redirect(authorization_url)
    else:
        auth_code = flask.request.args.get('code')
        print("code")
        print(auth_code)
        flow.fetch_token(authorization_response=auth_code)
        credentials = flow.credentials
        flask.session['credentials'] = {'token': credentials.token, 'refresh_token': credentials.refresh_token, 'token_uri': credentials.token_uri,
                                        'client_id': credentials.client_id, 'client_secret': credentials.client_secret, 'scopes': credentials.scopes}
        return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    app.run()
