import spotipy
import os
from spotipy import oauth2
from flask import jsonify
from flask import Flask, request

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
USERNAME = os.environ['USERNAME']
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'

seeds = ['spotify:track:6Yy9iylKlDwVuBnMEcmGYP']
playlist_scope = 'playlist-modify-public'
playlist_name = 'fresh grooves-alike-alike'
seed_playlist_id = 'seed_playlist_id'
limit = 15
port = 8080

sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=playlist_scope)

key_attrs = ['danceability', 'energy', 'valence']

other_attrs = ['key', 'mode', 'acousticness', 'instrumentalness', 'speechiness', 'tempo', 'time_signature']

access_token = None

track_uris = set()
unique_artist_map = {}


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
        try:
            sp = spotipy.Spotify(auth=access_token)
            # for seed_track in seeds:
            #     get_targeted_recs(sp, seed_track=[seed_track])
            create_similar_playlist(sp, seed_playlist_id)
        except Exception:
            raise
        return jsonify("nice")
    else:
        return jsonify("not great honestly")


def get_targeted_recs(sp: spotipy.Spotify, seed_track, rec_limit=limit):
    track_features = sp.audio_features(seed_track)[0]
    all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
    targets = {f'target_{k}': v for k, v in all_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **targets)
    tracks = [track['uri'] for track in recs['tracks']]
    track_uris.update(tracks)


# min/max the min/maxables, target everything else
def get_mixed_recs(sp: spotipy.Spotify, seed_track, variance, rec_limit=limit):
    track_features = sp.audio_features(seed_track)[0]
    adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
    other_track_stats = {k: v for k, v in track_features.items() if k in other_attrs}
    maxs = {f'max_{k}': min(round((variance * float(v)) + float(v), 3), 1.0) for k, v in adv_track_stats.items()}
    mins = {f'min_{k}': max(round(float(v) - (variance * float(v)), 3), 0.0) for k, v in adv_track_stats.items()}
    targets = {f'target_{k}': v for k, v in other_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **{**maxs, **mins, **targets})
    tracks = [track['uri'] for track in recs['tracks']]
    track_uris.update(tracks)


def get_fuzzy_recs(sp: spotipy.Spotify, seed_track, variance, rec_limit=limit):
    # track_stats = sp.track(seed_track[0])
    # artist_uris = [artist['uri'] for artist in track_stats['artists']]
    # genres = sp.artists(artist_uris)['artists'][0]['genres'][:5]
    track_features = sp.audio_features(seed_track)[0]
    adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
    maxs = {f'max_{k}': min(round((variance*float(v))+float(v), 3), 1.0) for k, v in adv_track_stats.items()}
    mins = {f'min_{k}': max(round(float(v)-(variance*float(v)), 3), 0.0) for k, v in adv_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **{**maxs, **mins})
    tracks = [track['uri'] for track in recs['tracks']]
    track_uris.update(tracks)


def create_playlist(sp: spotipy.Spotify):
    playlist_id = sp.user_playlist_create(USERNAME, playlist_name, public=True)['id']

    chunk_size = 100
    for i in range(0, len(track_uris), chunk_size):
        chunk = list(track_uris)[i:i+chunk_size]
        print(f'Adding {len(chunk)} tracks to playlist {playlist_name}')
        add_track_to_playlist(sp, tracks=chunk, username=USERNAME, playlist_id=playlist_id)


def create_similar_playlist(sp: spotipy.Spotify, playlist_id, max_songs_per_seed=5):
    playlist = sp.user_playlist_tracks(USERNAME, playlist_id, limit=100)
    playlist_tracks = [item['track']['uri'] for item in playlist['items']]
    for track in playlist_tracks:
        get_targeted_recs(sp, [track], rec_limit=max_songs_per_seed+1)
    create_playlist(sp)


def add_track_to_playlist(sp: spotipy.Spotify, tracks, username, playlist_id):
    sp.user_playlist_add_tracks(username, playlist_id, tracks)


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


if __name__ == '__main__':
    app.run(host='', port=port, debug=True)
