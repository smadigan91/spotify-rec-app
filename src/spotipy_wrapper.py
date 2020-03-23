import spotipy
from .models import *

# get playlists
# get recommendations given list of track objects (get their uris)


class SpotifyWrapper:

    def __init__(self, access_token):
        self.sp = spotipy.Spotify(auth=access_token)

    def get_playlist_tracks(self, playlist_id, track_limit=None):
        tracks = set()
        playlist = self.sp.playlist_tracks(playlist_id, limit=track_limit if track_limit and track_limit <= 100 else 100)
        tracks.update(Track(item['track']) for item in playlist['items'])
        offset = 0
        while playlist['next'] and (track_limit is None or track_limit != len(tracks)):
            limit = track_limit - len(tracks) if track_limit else 100
            offset = offset + 100
            playlist = self.sp.playlist_tracks(playlist_id, limit=limit if limit <= 100 else 100, offset=offset)
            tracks.update(Track(item['track']) for item in playlist['items'])
        return tracks

