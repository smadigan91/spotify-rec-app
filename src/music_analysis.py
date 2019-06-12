import spotipy
from collections import namedtuple, OrderedDict
from util import sort_dict_by_value, count_key
from typing import List

AverageAudioFeatures = namedtuple('AverageAudioFeatures', ['danceability', 'energy', 'speechiness',
                                                           'acousticness', 'valence', 'tempo'])
Artist = namedtuple('Artist', ['name', 'genres'])

primary_attribute_groups = ['scale', 'genre', 'artist']

key_pitch_map = {
    0: "C",
    1: "C♯/D♭",
    2: "D",
    3: "D♯/E♭",
    4: "E",
    5: "F",
    6: "F♯/G♭",
    7: "G",
    8: "G♯/A♭",
    9: "A",
    10: "A♯/B♭",
    11: "B"
}

mode_map = {
    1: "major",
    0: "minor"
}


class MusicAnalyzer:
    sp: spotipy.Spotify = None
    avg_audio_feats: List[AverageAudioFeatures] = []
    scales: List = []
    artists: List[Artist] = []
    scale_map = {}
    genre_map = {}
    artist_map = {}

    def __init__(self, user, access_token):
        self.user = user
        self.sp = spotipy.Spotify(auth=access_token)

    def generate_playlist_analysis(self, playlist_id, primary_key_attribute, use_strict_genres=False):
        if use_strict_genres:
            genres = self.sp.recommendation_genre_seeds()['genres']
        playlist_response = self.sp.user_playlist(self.user, playlist_id)
        playlist_name = playlist_response['name']
        title = f"Breakdown of '{playlist_name}' by {primary_key_attribute}"
        print(f"generating analysis by {primary_key_attribute}")
        self.index_playlist_tracks(playlist_id)
        results = self.crunch_numbers(primary_key_attribute, genre_list=genres)
        return {"title": title, "results": results}

    def generate_user_analysis(self, primary_key_attribute, use_strict_genres=False):
        if use_strict_genres:
            genres = self.sp.recommendation_genre_seeds()['genres']
        title = f"Breakdown of library by {primary_key_attribute}"
        print(f"generating analysis by {primary_key_attribute}")
        self.index_user_tracks()
        results = self.crunch_numbers(primary_key_attribute, genre_list=genres)
        return {"title": title, "results": results}

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

    def index_user_tracks(self):
        user_tracks = self.sp.current_user_saved_tracks()
        offset = 0
        while user_tracks['next']:
            print('Indexing 50 tracks and artists')
            self.index_data(user_tracks['items'])
            offset += 50
            user_tracks = self.sp.current_user_saved_tracks(limit=50, offset=offset)
        last_tracks = user_tracks['items']
        print(f"Indexing {len(last_tracks)} tracks and artists")
        self.index_data(last_tracks)

    def index_data(self, track_list: List):
        track_ids = []
        artist_ids = []
        for track_data in track_list:
            track = track_data['track']
            if track and not track['is_local']:
                artist_ids.append(track['artists'][0]['id'])
                track_ids.append(track['id'])
        print(f'indexing {len(track_list)} artists and audio features')
        half_artist_ids = len(artist_ids)//2
        artists = self.sp.artists(artists=artist_ids[half_artist_ids:])['artists']
        artists.extend(self.sp.artists(artists=artist_ids[:half_artist_ids])['artists'])
        for artist in artists:
            self.artists.append(Artist(name=artist['name'], genres=artist['genres']))
        audio_features_response = self.sp.audio_features(tracks=track_ids)
        for audio_feature in audio_features_response:
            self.avg_audio_feats.append(AverageAudioFeatures(danceability=audio_feature['danceability'],
                                                             energy=audio_feature['energy'],
                                                             speechiness=audio_feature['speechiness'],
                                                             acousticness=audio_feature['acousticness'],
                                                             valence=audio_feature['valence'],
                                                             tempo=audio_feature['tempo']))
            txt_scale = f"{key_pitch_map[audio_feature['key']]} {mode_map[audio_feature['mode']]}"
            self.scales.append(txt_scale)

    def crunch_numbers(self, primary_key_attribute, genre_list=None):
        if not (len(self.artists) == len(self.scales) == len(self.avg_audio_feats)):
            raise RuntimeError(f"Length of indices not equal - artists: {len(self.artists)}, scales: "
                               f"{len(self.scales)}, audio_features: {len(self.avg_audio_feats)}")
        if primary_key_attribute not in primary_attribute_groups:
            raise RuntimeError(f"Primary attribute should be one of: {', '.join(primary_attribute_groups)}")

        result = {}
        if 'genre' in primary_key_attribute:
            print('crunching numbers by genre...')
            result = self.genre_map
            for i in range(len(self.artists)):
                artist: Artist = self.artists[i]
                avg_feats: AverageAudioFeatures = self.avg_audio_feats[i]
                scale = self.scales[i]
                genres = artist.genres
                for genre in genres:
                    secondary_key_attributes = {
                        'scale': scale,
                        'artist': artist.name
                    }
                    if genre_list:
                        if genre in genre_list:
                            # for every genre, index the genre as a primary key attribute and feed the key_attributes map
                            self.index_primary_key_attribute_value(result, genre, avg_feats, secondary_key_attributes, genre_list)
                    else:
                        self.index_primary_key_attribute_value(result, genre, avg_feats, secondary_key_attributes)
        elif 'artist' in primary_key_attribute:
            print('crunching numbers by artist...')
            result = self.artist_map
            for i in range(len(self.artists)):
                artist: Artist = self.artists[i]
                avg_feats: AverageAudioFeatures = self.avg_audio_feats[i]
                scale = self.scales[i]
                genres = artist.genres
                secondary_key_attributes = {
                    'scale': scale,
                    'genres': genres
                }
                self.index_primary_key_attribute_value(result, artist.name, avg_feats, secondary_key_attributes, genre_list)
        elif 'scale' in primary_key_attribute:
            print('crunching numbers by key and mode...')
            result = self.scale_map
            for i in range(len(self.artists)):
                artist: Artist = self.artists[i]
                avg_feats: AverageAudioFeatures = self.avg_audio_feats[i]
                scale = self.scales[i]
                genres = artist.genres
                secondary_key_attributes = {
                    'artist': artist.name,
                    'genres': genres
                }
                self.index_primary_key_attribute_value(result, scale, avg_feats, secondary_key_attributes, genre_list)
        self.clean_primary_key_attributes(result)
        return OrderedDict(sorted(result.items(), key=lambda kv: kv[1]['count'], reverse=True))

    def index_primary_key_attribute_value(self, dct, primary_key_attribute_val, avg_feats, secondary_key_attributes, genre_list=None):
        data = dct.get(primary_key_attribute_val)
        if data:
            data['count'] += 1
            data['avg_attributes'].append(avg_feats)
            self.index_secondary_key_attributes(data['key_attributes'], secondary_key_attributes, genre_list=genre_list)
        else:
            data = dict()
            data['count'] = 1
            data['avg_attributes'] = [avg_feats]
            data['key_attributes'] = self.index_secondary_key_attributes({}, secondary_key_attributes, genre_list=genre_list)
            dct[primary_key_attribute_val] = data

    def index_secondary_key_attributes(self, dct, secondary_key_attributes, genre_list=None):
        for secondary_key_attribute_name, secondary_key_attribute_val in secondary_key_attributes.items():
            if not secondary_key_attribute_name == 'genres':
                self.index_secondary_key_attribute_value(dct, secondary_key_attribute_name, secondary_key_attribute_val)
            else:
                for genre in secondary_key_attribute_val:
                    if genre_list:
                        if genre in genre_list:
                            # index each genre separately
                            self.index_secondary_key_attribute_value(dct, secondary_key_attribute_name, genre)
                    else:
                        self.index_secondary_key_attribute_value(dct, secondary_key_attribute_name, genre)
        return dct

    def index_secondary_key_attribute_value(self, key_attributes, key_attribute_name, key_attribute_value):
        secondary_key_attribute_count_dct = key_attributes.get(key_attribute_name)
        if secondary_key_attribute_count_dct:
            # if there is a pre-existing counting dict for this attribute name, count the corresponding value
            count_key(secondary_key_attribute_count_dct, key_attribute_value)
        else:
            key_attributes[key_attribute_name] = {key_attribute_value: 1}
        return key_attributes

    # sum averages, sort secondary key attributes
    def clean_primary_key_attributes(self, primary_key_attributes):
        for data in primary_key_attributes.values():
            data['avg_attributes'] = self.sum_averages(data['avg_attributes'])
            self.sort_secondary_key_attributes(data['key_attributes'])

    # sum averages, sort nested key/value dicts, sort outer primary dict
    def sort_secondary_key_attributes(self, secondary_key_attributes):
        for secondary_key_attribute_name, secondary_key_attribute_count_dct in secondary_key_attributes.items():
            secondary_key_attributes[secondary_key_attribute_name] = \
                sort_dict_by_value(secondary_key_attribute_count_dct)

    # combine a list of groupings of averageable attributes into one dict representing averages
    def sum_averages(self, average_attributes_list):
        avg_attribute: AverageAudioFeatures
        total = len(average_attributes_list)
        danceability = 0
        energy = 0
        speechiness = 0
        acousticness = 0
        valence = 0
        tempo = 0
        for avg_attribute in average_attributes_list:
            danceability += avg_attribute.danceability
            energy += avg_attribute.energy
            speechiness += avg_attribute.speechiness
            acousticness += avg_attribute.acousticness
            valence += avg_attribute.valence
            tempo += avg_attribute.tempo
        return {'danceability': round(danceability/total, 3),
                'energy': round(energy/total, 3),
                'speechiness': round(speechiness/total, 3),
                'acousticness': round(acousticness/total, 3),
                'valence': round(valence/total, 3),
                'tempo': round(tempo/total, 3)}




