import flask
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

mod_auth = flask.Blueprint('auth', __name__, url_prefix='/auth')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


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
    flask.session['saveStatus'] = 'connected'
    return flask.redirect(flask.url_for('index'))


@mod_auth.route('/account')
def account():
    accountStatus = {
        # 'saveStatus': flask.session.get('saveStatus', 'not_connected'),
        # for front-end development use:
        'saveStatus': 'up_to_date',
        'progressURL': flask.session.get('progressURL', '')
    }
    print(accountStatus)
    return json.dumps(accountStatus), 200, {'ContentType': 'application/json'}


@mod_auth.route('/disconnect')
def disconnect():
    flask.session.pop('credentials')
    flask.session['saveStatus'] = 'not_connected'
    return flask.redirect(flask.url_for('write.clear'))
