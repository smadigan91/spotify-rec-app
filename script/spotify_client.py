import spotipy
import os
import webbrowser
import threading
from spotipy import oauth2
from flask import jsonify
from flask import Flask, request

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
USERNAME = os.environ['USERNAME']
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'

seeds = ['spotify:track:6Yy9iylKlDwVuBnMEcmGYP']
scope = 'playlist-modify-public user-top-read'
playlist_name = "playlist_name"
seed_playlist_id = 'seed_playlist_id'
limit = 15
port = 8080

# pay attention to the scope you're passing here - look in spotify web api reference to see if its correct for the call
sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)

key_attrs = ['danceability', 'energy', 'valence']

other_attrs = ['key', 'mode', 'acousticness', 'instrumentalness', 'speechiness', 'tempo', 'time_signature']

access_token = None

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
        if access_token:
            print("Successfully acquired access token! Now doing the thing with the stuff")
        try:
            sp = spotipy.Spotify(auth=access_token)
            # for seed_track in seeds:
            #     get_targeted_recs(sp, seed_track=[seed_track])
            # create_similar_playlist(sp, playlist_id=seed_playlist_id, max_recs_per_seed=5, max_tracks_per_artist=1)
            get_top_tracks(sp, print_output=True, time_range='short_term')
        except Exception:
            raise
        return jsonify("nice")
    else:
        return jsonify("not great honestly")


def get_targeted_recs(sp: spotipy.Spotify, seed_track, rec_limit=limit, max_tracks_per_artist=None):
    track_features = sp.audio_features(seed_track)[0]
    all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
    targets = {f'target_{k}': v for k, v in all_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **targets)
    rec_tracks = extract_rec_tracks(recs, max_tracks_per_artist)
    # remove the track(s) we're getting recommendations for
    for track in seed_track:
        if track in rec_tracks:
            rec_tracks.remove(track)
    return set(rec_tracks)


# min/max the min/maxables, target everything else
def get_mixed_recs(sp: spotipy.Spotify, seed_track, variance, rec_limit=limit, max_tracks_per_artist=None):
    track_features = sp.audio_features(seed_track)[0]
    adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
    other_track_stats = {k: v for k, v in track_features.items() if k in other_attrs}
    maxs = {f'max_{k}': min(round((variance * float(v)) + float(v), 3), 1.0) for k, v in adv_track_stats.items()}
    mins = {f'min_{k}': max(round(float(v) - (variance * float(v)), 3), 0.0) for k, v in adv_track_stats.items()}
    targets = {f'target_{k}': v for k, v in other_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **{**maxs, **mins, **targets})
    rec_tracks = extract_rec_tracks(recs, max_tracks_per_artist)
    # remove the track(s) we're getting recommendations for
    for track in seed_track:
        if track in rec_tracks:
            rec_tracks.remove(track)
    return set(rec_tracks)


def get_fuzzy_recs(sp: spotipy.Spotify, seed_track, variance, rec_limit=limit, max_tracks_per_artist=None):
    # track_stats = sp.track(seed_track[0])
    # artist_uris = [artist['uri'] for artist in track_stats['artists']]
    # genres = sp.artists(artist_uris)['artists'][0]['genres'][:5]
    track_features = sp.audio_features(seed_track)[0]
    adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
    maxs = {f'max_{k}': min(round((variance*float(v))+float(v), 3), 1.0) for k, v in adv_track_stats.items()}
    mins = {f'min_{k}': max(round(float(v)-(variance*float(v)), 3), 0.0) for k, v in adv_track_stats.items()}

    recs = sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **{**maxs, **mins})
    rec_tracks = extract_rec_tracks(recs, max_tracks_per_artist)
    # remove the track(s) we're getting recommendations for
    for track in seed_track:
        if track in rec_tracks:
            rec_tracks.remove(track)
    return set(rec_tracks)


# assumes track and artist uri tuple passed in
def get_songs_per_artist(rec_track_tuples_list, max_tracks_per_artist=None):
    artist_map = {}
    track_uris = []
    for track_artist_tuple in rec_track_tuples_list:
        artist = track_artist_tuple[1]
        if artist not in artist_map:
            artist_map[artist] = [track_artist_tuple[0]]
        else:
            if max_tracks_per_artist:
                if len(artist_map[artist]) < max_tracks_per_artist:
                    artist_map[artist].append(track_artist_tuple[0])
            else:
                artist_map[artist].append(track_artist_tuple[0])
    for tracks in artist_map.values():
        track_uris.extend(tracks)
    return track_uris


def extract_rec_tracks(recs, max_tracks_per_artist=None):
    if not max_tracks_per_artist:
        rec_tracks = [track['uri'] for track in recs['tracks']]
    else:
        rec_tracks_tuples_list = extract_track_artist_tuples_list(recs)
        rec_tracks = get_songs_per_artist(rec_tracks_tuples_list, max_tracks_per_artist)
    return rec_tracks


def extract_track_artist_tuples_list(recs):
    rec_tracks_tuples_list = [(track['uri'], track['artists'][0]['uri']) for track in recs['tracks']]
    return rec_tracks_tuples_list


# playlist stuff


def add_track_to_playlist(sp: spotipy.Spotify, tracks, username, playlist_id):
    sp.user_playlist_add_tracks(username, playlist_id, tracks)


def create_playlist(sp: spotipy.Spotify, track_uris):
    playlist_id = sp.user_playlist_create(USERNAME, playlist_name, public=True)['id']

    chunk_size = 100
    for i in range(0, len(track_uris), chunk_size):
        chunk = list(track_uris)[i:i+chunk_size]
        print(f'Adding {len(chunk)} tracks to playlist {playlist_name}')
        add_track_to_playlist(sp, tracks=chunk, username=USERNAME, playlist_id=playlist_id)


def create_similar_playlist(sp: spotipy.Spotify, playlist_id, max_recs_per_seed=5, max_tracks_per_artist=None):
    playlist = sp.user_playlist_tracks(USERNAME, playlist_id, limit=100)
    playlist_tracks = [item['track']['uri'] for item in playlist['items']]
    rec_tracks = set()
    tuples_list = []
    # for each track in the playlist, fetch up to a number of recommended tracks
    for track in playlist_tracks:
        seed_track = [track]
        # TODO register callback so filtering methtod isnt hardcoded
        track_features = sp.audio_features(seed_track)[0]
        all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
        targets = {f'target_{k}': v for k, v in all_track_stats.items()}

        recs = sp.recommendations(seed_tracks=seed_track, limit=max_recs_per_seed, **targets)
        if max_tracks_per_artist:
            # if max_tracks_per_artist specified, cache artist data too for later filtering
            track_artist_tuples_list = extract_track_artist_tuples_list(recs)
            tuples_list.extend(track_artist_tuples_list)
        else:
            # otherwise just add all thet track uris to the recommened list
            rec_uris = [track['uri'] for track in recs['tracks']]
            rec_tracks.update(rec_uris)
    if max_tracks_per_artist:
        # if max_tracks_per_artist specified, filter by given value
        rec_tracks.update(get_songs_per_artist(tuples_list, max_tracks_per_artist))
    # remove any tracks from original playlist as well. Doesn't always work for some reason (I blame spotify)
    for track in playlist_tracks:
        if track in rec_tracks:
            rec_tracks.remove(track)
    create_playlist(sp, track_uris=rec_tracks)


# Top artists / tracks


def get_top_tracks(sp: spotipy.Spotify, track_limit=50, time_range='medium_term', print_output=False):
    top_tracks = sp.current_user_top_tracks(limit=track_limit, time_range=time_range)
    track_tuples = [(track['name'], track['artists'][0]['name']) for track in top_tracks['items']]
    if print_output:
        print(f'Top {track_limit} tracks for current user in {time_range} timeframe:')
        print('{:<70}{}'.format('Track Name', 'Artist'))
        for track_tuple in track_tuples:
            print('{:<70}{}'.format(track_tuple[0], track_tuple[1]))


def get_top_artists(sp: spotipy.Spotify, artist_limit=50, time_range='medium_term', print_output=False):
    top_artists = sp.current_user_top_artists(limit=artist_limit, time_range=time_range)
    artist_tuples = [(artist['name'], artist['genres']) for artist in top_artists['items']]
    if print_output:
        print(f'Top {artist_limit} artists for current user in {time_range} timeframe:')
        print('{:<50}{}'.format('Artist Name', 'Genres'))
        for track_tuple in artist_tuples:
            print('{:<50}{}'.format(track_tuple[0], track_tuple[1]))


def html_for_login_button():
    auth_url = get_spotify_oauth_url()
    html_login_button = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return html_login_button


def get_spotify_oauth_url():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


if __name__ == '__main__':
    threading.Thread(target=app.run, args=('', port)).start()
    webbrowser.open(url=f'{SPOTIFY_REDIRECT_URI}auth', new=2, autoraise=True)
