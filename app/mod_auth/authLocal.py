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
    credentials = flow.run_local_server(port=5001)
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}
    return flask.redirect(flask.url_for('index'))
