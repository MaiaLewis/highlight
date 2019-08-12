import flask
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

mod_auth = flask.Blueprint('auth', __name__, url_prefix='/auth')
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


@mod_auth.route('/oauth2callback')
def oauth2callback():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials_local.json', SCOPES)
    print("hi")
    credentials = flow.run_local_server(port=5001)
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}
    print("Session")
    print(flask.session)
    return flask.redirect(flask.url_for('index'))


@mod_auth.route('/areCredentials')
def areCredentials():
    print("Session")
    print(flask.session)
    if 'credentials' in flask.session:
        response = {"areCredentials": "true"}
    else:
        response = {"areCredentials": "false"}
    response = json.dumps(response)
    return response


@mod_auth.route('/account')
def account():
    status = []
    if 'credentials' in flask.session:
        status.append("credentials")
    if 'docsSaved' in flask.session:
        status.append("docsSaved")
    response = json.dumps(status)
    return response


@mod_auth.route('/disconnect')
def disconnect():
    flask.session.pop('credentials')
    flask.session.pop('docsSaved')
    return flask.redirect(flask.url_for('save.clear'))
