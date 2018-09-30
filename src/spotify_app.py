import webbrowser
import threading
from spotify_auth import *
from flask import jsonify
from flask import Flask, request
from spotipy_wrapper import SpotipyWrapper

app = Flask(__name__)
sp_auth = SpotifyAuth()

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'
app_port = 8080

# get cached token from redis, key by bose email or something, only prompt to log into spotify if not found in cache


@app.route("/auth")
def auth():
    return html_for_login_button()


@app.route("/")
def index():
    url = request.url
    code = url.split("?code=")[1].split("&")[0]
    if code:
        print("Fetching access token")
        access_token = sp_auth.get_fresh_token(code)
        try:
            sp = SpotipyWrapper(access_token)
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
    seed_playlist_id = 'playlist_id'
    sp.create_similar_playlist(playlist_id=seed_playlist_id, max_recs_per_seed=5, max_tracks_per_artist=3)


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_auth.get_authorize_url()
    return auth_url


if __name__ == '__main__':
    threading.Thread(target=app.run, args=('', app_port)).start()
    # app.run(host='', port=port)
    webbrowser.open(url=f'{SPOTIFY_REDIRECT_URI}auth', new=2, autoraise=True)
