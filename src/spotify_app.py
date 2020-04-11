import os
import webbrowser
import threading
import json
from spotipy import oauth2
from flask import jsonify
from flask import Flask, request
from spotipy_wrapper import SpotipyWrapper
from music_analysis import MusicAnalyzer

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = 'http://localhost:9090/'

scope = 'playlist-modify-public user-top-read user-library-read'
user = os.environ['USERNAME']
port = 9090

# pay attention to the scope you're passing here - look in spotify web api reference to see if its correct for the call
sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, username=user,
                               scope=scope)

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
        print("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        if access_token:
            print("Successfully acquired access token! Now doing the thing with the stuff")
        try:
            ma = MusicAnalyzer(user, access_token)
            data = do_ma_callback(ma)
            return data
            # sp = SpotipyWrapper(user, access_token)
            # do_sp_callback(sp)
        except Exception:
            raise
        # return jsonify("nice")
    else:
        return jsonify("not great honestly")


def do_ma_callback(ma: MusicAnalyzer):
    print('doing the thing')
    playlist_id = '3mvk6VQchnKTX0mwyLtIZb'
    primary_attribute_group = 'genre'
    result = ma.generate_playlist_analysis(playlist_id=playlist_id, primary_key_attribute=primary_attribute_group)
    data = json.dumps(result)
    print('done')
    return data


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


if __name__ == '__main__':
    threading.Thread(target=app.run, args=('', port)).start()
    # app.run(host='', port=port)
    webbrowser.open(url=f'{SPOTIFY_REDIRECT_URI}auth', new=2, autoraise=True)
