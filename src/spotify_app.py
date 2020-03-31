import logging as log
from flask import Flask, request, jsonify, session, Response, render_template, redirect, url_for
from flask_session import Session
from datetime import timedelta
from spotipy import oauth2
from .spotipy_wrapper import SpotifyWrapper
from .config import *
from .models import ModelValidationException, RecSpec

app = Flask(__name__)
log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
app.logger = log
app.secret_key = SESSION_KEY
SESSION_TYPE = 'redis'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = get_redis_connection()
sess = Session()
sess.init_app(app)
app.permanent_session_lifetime = timedelta(minutes=30)

SPOTIFY_CLIENT_ID = SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = SPOTIFY_CLIENT_SECRET
# can only be run locally for now
HOST = 'http://localhost'
BASE_PORT = 8080
BASE_URL = f'{HOST}:{BASE_PORT}'
SPOTIFY_REDIRECT_URI = f'{BASE_URL}/auth'
scope = 'playlist-modify-public user-top-read'

sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)


def default_exception_handler(exception):
    exception_name = type(exception).__name__
    log.error("{}: {} ".format(exception_name, exception), exc_info=True)
    return jsonify({'something went wrong': exception_name}), 500


def validation_exception_handler(exception: ModelValidationException):
    return jsonify({'error': exception.message}), 400


app.register_error_handler(ModelValidationException, validation_exception_handler)
app.register_error_handler(ModelValidationException, validation_exception_handler)
app.register_error_handler(Exception, default_exception_handler)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify("page not found"), 404


@app.route("/login")
def login():
    return render_template('login.html', spotify_auth_url=get_spotify_oauth_url())

# TODO prevent refreshing on undefined route (like /page2) from borking app
@app.route("/main")
def main():
    return render_template('main.html')


@app.route("/auth")
def auth():
    url = request.url
    code = sp_oauth.parse_response_code(url)
    if code:
        log.info("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        access_token = token_info['access_token']
        if access_token:
            log.info("Successfully acquired access token! Saving it in the session")
            set_session_token(access_token)
            return redirect(f'{BASE_URL}{url_for("form")}')
        else:
            return jsonify("No access token found in spotify token info"), 500
    else:
        return jsonify("No auth code returned by spotify"), 500


@app.route("/form")
def form():
    return render_template('form.html', base_url=BASE_URL)


@app.route("/generate", methods=['POST'])
def generate_recs():
    request_json = request.get_json(force=True, silent=False)
    access_token = get_session_token()
    if not access_token:
        log.error("Session has expired")
        return jsonify("Session has expired"), 401
    else:
        log.info(f"Request json: {request_json}")
        rec_spec = RecSpec(request_json)
        sp = SpotifyWrapper(access_token, log)
        sp.generate_recommendations(rec_spec)
        return jsonify("Looks like it worked, nice"), 200


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


def get_session_token():
    return session.get('access_token', None)


def set_session_token(access_token):
    session['access_token'] = access_token
