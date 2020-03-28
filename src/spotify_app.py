import logging as log
from flask import Flask, request, jsonify, session, Response, render_template, redirect, url_for
from flask_session import Session
from datetime import timedelta
from spotipy import oauth2
from .spotipy_wrapper import SpotifyWrapper
from .config import *

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

# get username from initial auth code and initialize oauth and wrapper
sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)


@app.route("/index")
def index():
    return render_template('index.html', spotify_auth_url=get_spotify_oauth_url())


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
            return redirect(f'{BASE_URL}{url_for("generate_recs")}')
        else:
            return jsonify("No access token found in spotify token info"), 500
    else:
        return jsonify("No auth code returned by spotify"), 500


@app.route("/generate")
def generate_recs():
    access_token = get_session_token()
    if not access_token:
        log.error("Session has expired")
        return jsonify("Session has expired"), 401
    else:
        log.info("Generating stuff")
        try:
            sp = SpotifyWrapper(access_token)
            do_callback(sp)
        except Exception:
            raise
        return jsonify("Looks like it worked, nice"), 200


def do_callback(sp: SpotifyWrapper):
    # this is just printing the tracks to my 'Best of Ween' playlist right now lol
    log.info('doing the thing')
    playlist_id = '5cgfIBf7Fc2iHcjIj2zMUe'
    playlist_tracks = sp.get_playlist_tracks(playlist_id)
    for track in playlist_tracks:
        log.info(track.name)
    log.info('done')


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


def get_session_token():
    return session.get('access_token', None)


def set_session_token(access_token):
    session['access_token'] = access_token
