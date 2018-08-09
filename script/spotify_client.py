import spotipy
from spotipy import oauth2
from flask import jsonify
from flask import Flask, request

app = Flask(__name__)

SPOTIFY_CLIENT_ID = 'XXXXXXXXXXXXXXXXXXXXXX'
SPOTIFY_CLIENT_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXX'
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'

# this is Zoom! by Super Furry Animals
seed = ['spotify:track:5bY91ggHChDPiNtzW729Hn']
playlist_scope = 'playlist-modify-private'
limit = 20
port = 8080

sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=playlist_scope)

key_attrs = ['danceability', 'energy', 'valence']

other_attrs = ['key', 'mode', 'acousticness', 'instrumentalness', 'speechiness', 'tempo', 'time_signature']

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
        try:
            get_fuzzy_recs(access_token, seed_track=seed, variance=0.2)
        except Exception:
            raise
        return jsonify("nice")
    else:
        return jsonify("not great honestly")


def get_targeted_recs(token, seed_track):
    sp = spotipy.Spotify(auth=token)
    track_features = sp.audio_features(seed_track)[0]
    all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
    targets = {f'target_{k}': v for k, v in all_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=100, **targets)
    tracks = [(track['name'], track['artists'][0]['name'], track['uri']) for track in recs['tracks']]
    for idx, track in enumerate(tracks):
        print(idx+1, track)


# min/max the min/maxables, target everything else
def get_mixed_recs(token, seed_track, variance):
    sp = spotipy.Spotify(auth=token)
    track_features = sp.audio_features(seed_track)[0]
    adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
    other_track_stats = {k: v for k, v in track_features.items() if k in other_attrs}
    maxs = {f'max_{k}': min(round((variance * float(v)) + float(v), 3), 1.0) for k, v in adv_track_stats.items()}
    mins = {f'min_{k}': max(round(float(v) - (variance * float(v)), 3), 0.0) for k, v in adv_track_stats.items()}
    targets = {f'target_{k}': v for k, v in other_track_stats.items()}
    print(targets)
    print(maxs)
    print(mins)

    recs = sp.recommendations(seed_tracks=seed_track, limit=100, **{**maxs, **mins, **targets})
    tracks = [(track['name'], track['artists'][0]['name'], track['uri']) for track in recs['tracks']]
    for idx, track in enumerate(tracks):
        print(idx+1, track)


def get_fuzzy_recs(token, seed_track, variance):
    sp = spotipy.Spotify(auth=token)
    # track_stats = sp.track(seed_track[0])
    # artist_uris = [artist['uri'] for artist in track_stats['artists']]
    # genres = sp.artists(artist_uris)['artists'][0]['genres'][:5]
    track_features = sp.audio_features(seed_track)[0]
    adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
    maxs = {f'max_{k}': min(round((variance*float(v))+float(v), 3), 1.0) for k, v in adv_track_stats.items()}
    mins = {f'min_{k}': max(round(float(v)-(variance*float(v)), 3), 0.0) for k, v in adv_track_stats.items()}
    print(maxs)
    print(mins)

    recs = sp.recommendations(seed_tracks=seed_track, limit=100, **{**maxs, **mins})
    tracks = [(track['name'], track['artists'][0]['name'], track['uri']) for track in recs['tracks']]
    for idx, track in enumerate(tracks):
        print(idx+1, track)


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


if __name__ == '__main__':
    app.run(host='', port=port, debug=True)
