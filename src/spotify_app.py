import os
import logging as logger
from spotipy import oauth2
from flask import jsonify
from flask import Flask, request
from .spotipy_wrapper import SpotifyWrapper

app = Flask(__name__)
logger.basicConfig(format='%(levelname)s: %(message)s', level=logger.INFO)
app.logger = logger

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
# can only be run locally for now
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'
scope = 'playlist-modify-public user-top-read'
user = os.environ['USERNAME']
port = 8080

# get username from initial auth code and initialize oauth and wrapper
sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope,
                               cache_path=".cache")

access_token = None


@app.route("/auth")
def auth():
    return html_for_login_button()


@app.route("/")
def index():
    global access_token
    url = request.url
    code = sp_oauth.parse_response_code(url)
    if code:
        logger.info("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        if access_token:
            logger.info("Successfully acquired access token! Now doing the thing with the stuff")
        try:
            sp = SpotifyWrapper(access_token)
            do_callback(sp)
        except Exception:
            raise
        return jsonify("nice")
    else:
        return jsonify("not great honestly")


def do_callback(sp: SpotifyWrapper):
    # this is just printing the tracks to my 'Best of Ween' playlist right now lol
    logger.info('doing the thing')
    playlist_id = '5cgfIBf7Fc2iHcjIj2zMUe'
    playlist_tracks = sp.get_playlist_tracks(playlist_id)
    for track in playlist_tracks:
        logger.info(track.name)
    logger.info('done')


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
