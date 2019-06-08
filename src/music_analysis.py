import spotipy
from collections import namedtuple
from util import safeget
from typing import List

AverageAudioFeatures = namedtuple('AverageAudioFeatures', ['danceability', 'energy', 'loudness', 'speechiness',
                                                           'acousticness', 'valence', 'tempo'])
KeyAudioFeatures = namedtuple('KeyAudioFeatures', ['key', 'mode'])
Artist = namedtuple('Artist', ['name', 'genres'])


class MusicAnalyzer:
    sp: spotipy.Spotify = None
    avg_audio_feats: List[AverageAudioFeatures] = []
    key_audio_feats: List[KeyAudioFeatures] = []
    artists: List[Artist] = []

    def __init__(self, user, access_token):
        self.user = user
        self.sp = spotipy.Spotify(auth=access_token)

    def index_playlist_tracks(self, playlist_id):
        playlist = self.sp.user_playlist_tracks(self.user, playlist_id)
        offset = 0
        while playlist['next']:
            print('Indexing 100 tracks and artists')
            self.index_data(playlist['items'])
            offset += 100
            playlist = self.sp.user_playlist_tracks(self.user, playlist_id, offset=offset)
        last_tracks = playlist['items']
        print(f"Indexing {len(last_tracks)} tracks and artists")
        self.index_data(last_tracks)
        # serialize playlist tracks one last time, return

    def index_data(self, track_list: List):
        track_ids = []
        artist_ids = []
        for track in track_list:
            if track and not track['is_local']:
                artist_ids.append(track['artists'][0]['id'])
                track_ids.append(track['id'])
        print(f'indexing {len(track_list)} artists and audio features')
        artist_response = self.sp.artists(artists=artist_ids)
        for artist in artist_response['artists']:
            self.artists.append(Artist(name=artist['name'], genres=artist['genres']))
        audio_features_response = self.sp.audio_features(tracks=track_ids)
        for audio_feature in audio_features_response["audio_features"]:
            self.avg_audio_feats.append(AverageAudioFeatures(danceability=audio_feature['danceability'],
                                                             energy=audio_feature['energy'],
                                                             loudness=audio_feature['loudness'],
                                                             speechiness=['speechiness'],
                                                             acousticness=['acousticness'],
                                                             valence=['valence'],
                                                             tempo=['tempo']))
            self.key_audio_feats.append(KeyAudioFeatures(key=audio_feature['key'], mode=audio_feature['mode']))



    # walk through all lists in sequence
    # have unique key attribute maps
    # have key attributes from objects in each list handy, including every genre for the artist
    # add list of average objects to key attribute to be averaged together later
    # add all other key attributes to key_attributes and increment their value's occurence for that key attribuute

    # do average calculations for all key attributes after the fact by taking the list of average attributes objects
    # and summing their values then dividing by the total number, then adding mappings to map



