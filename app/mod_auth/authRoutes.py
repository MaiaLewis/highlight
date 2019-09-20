import flask
import os
from google_auth_oauthlib.flow import Flow
import json

mod_auth = flask.Blueprint('auth', __name__, url_prefix='/auth')


@mod_auth.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive.readonly'],
        redirect_uri=flask.url_for('auth.oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline')
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
        flask.session['saveStatus'] = 'connected'
        return flask.redirect(flask.url_for('index'))


@mod_auth.route('/account')
def account():
    accountStatus = {
        'saveStatus': flask.session.get('saveStatus', 'not_connected'),
        'progressURL': flask.session.get('progressURL', '')
    }
    print(accountStatus)
    return json.dumps(accountStatus), 200, {'ContentType': 'application/json'}


@mod_auth.route('/disconnect')
def disconnect():
    flask.session.pop('credentials')
    flask.session['saveStatus'] = 'not_connected'
    return flask.redirect(flask.url_for('write.clear'))
