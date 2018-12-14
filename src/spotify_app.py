import os
import webbrowser
import threading
from spotipy import oauth2
from flask import jsonify
from flask import Flask, request
from spotipy_wrapper import SpotipyWrapper

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'

scope = 'playlist-modify-public user-top-read'
user = os.environ['USERNAME']
port = 8080

# pay attention to the scope you're passing here - look in spotify web api reference to see if its correct for the call
sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)

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
            sp = SpotipyWrapper(user, access_token)
            do_callback(sp)
        except Exception:
            raise
        return jsonify("nice")
    else:
        return jsonify("not great honestly")


# interesting code goes here
def do_callback(sp: SpotipyWrapper):
    # get the top 5 recs for each of the top 100 tracks in the short term with two maximum songs per artist returned
    # rec_tracks = sp.get_top_recs(track_limit=100, time_range='long_term', max_recs_per_seed=5, max_tracks_per_artist=2)
    # sp.create_playlist(rec_tracks)
    # seed_playlist_id = '1rE0mogWXb3nX0szdJZRCm'
    # sp.create_similar_playlist(playlist_id=seed_playlist_id, max_recs_per_seed=30, max_tracks_per_artist=1)
    print('doing the thing')
    seed_tracks = ['4eWIU1wbuWrcgQsDT3aH47']
    sp.create_radio_playlist(seed_tracks=seed_tracks, max_recs_per_seed=5, depth=5)
    print('done')


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
