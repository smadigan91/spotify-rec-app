import spotipy
import os


key_attrs = ['danceability', 'energy', 'valence']

other_attrs = ['key', 'mode', 'acousticness', 'instrumentalness', 'speechiness', 'tempo', 'time_signature']

divisible_attrs = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'speechiness', 'tempo']

non_divisible_attrs = ['key', 'mode', 'time_signature']

USERNAME = os.environ['USERNAME']

seeds = ['spotify:track:6Yy9iylKlDwVuBnMEcmGYP']
playlist_name = "playlist_name"
seed_playlist_id = 'seed_playlist_id'
limit = 15


class SpotipyWrapper:

    sp: spotipy.Spotify = None

    def __init__(self, access_token):
        self.sp = spotipy.Spotify(auth=access_token)

    def get_targeted_recs(self, seed_track, rec_limit=limit, max_tracks_per_artist=None):
        """
        uses target_* for each attribute
        :param seed_track: the track to generate recommendations from
        :param rec_limit: max number of recommendations per track, up to 100
        :param max_tracks_per_artist: max number of tracks per artist in recommendations
        :return: a set of the recommended tracks
        """
        track_features = self.sp.audio_features(seed_track)[0]
        all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
        targets = {f'target_{k}': v for k, v in all_track_stats.items()}

        recs = self.sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **targets)
        rec_tracks = self.extract_rec_tracks(recs, max_tracks_per_artist)
        # remove the track(s) we're getting recommendations for
        for track in seed_track:
            if track in rec_tracks:
                rec_tracks.remove(track)
        return set(rec_tracks)

    def get_mixed_recs(self, seed_track, variance, rec_limit=limit, max_tracks_per_artist=None):
        """
        max_*/min_* key attributes by +/- variance%, target_* everything else
        :param seed_track: the track to generate recommendations from
        :param variance: percentage to vary max/min by relative to base (e.g. 0.2 means +/-20% of the original value)
        :param rec_limit: max number of recommendations per track, up to 100
        :param max_tracks_per_artist: max number of tracks per artist in recommendations
        :return: a set of the recommended tracks
        """
        track_features = self.sp.audio_features(seed_track)[0]
        adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
        other_track_stats = {k: v for k, v in track_features.items() if k in other_attrs}
        maxs = {f'max_{k}': min(round((variance * float(v)) + float(v), 3), 1.0) for k, v in adv_track_stats.items()}
        mins = {f'min_{k}': max(round(float(v) - (variance * float(v)), 3), 0.0) for k, v in adv_track_stats.items()}
        targets = {f'target_{k}': v for k, v in other_track_stats.items()}

        recs = self.sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **{**maxs, **mins, **targets})
        rec_tracks = self.extract_rec_tracks(recs, max_tracks_per_artist)
        # remove the track(s) we're getting recommendations for
        for track in seed_track:
            if track in rec_tracks:
                rec_tracks.remove(track)
        return set(rec_tracks)

    def get_fuzzy_recs(self, seed_track, variance, rec_limit=limit, max_tracks_per_artist=None):
        """
        :param seed_track: the track to generate recommendations from
        :param variance: percentage to vary max/min by relative to base (e.g. 0.2 means +/-20% of the original value)
        :param rec_limit: max number of recommendations per track, up to 100
        :param max_tracks_per_artist: max number of tracks per artist in recommendations
        :return: a set of the recommended tracks
        """
        # track_stats = self.sp.track(seed_track[0])
        # artist_uris = [artist['uri'] for artist in track_stats['artists']]
        # genres = self.sp.artists(artist_uris)['artists'][0]['genres'][:5]
        track_features = self.sp.audio_features(seed_track)[0]
        adv_track_stats = {k: v for k, v in track_features.items() if k in key_attrs}
        maxs = {f'max_{k}': min(round((variance*float(v))+float(v), 3), 1.0) for k, v in adv_track_stats.items()}
        mins = {f'min_{k}': max(round(float(v)-(variance*float(v)), 3), 0.0) for k, v in adv_track_stats.items()}

        recs = self.sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **{**maxs, **mins})
        rec_tracks = self.extract_rec_tracks(recs, max_tracks_per_artist)
        # remove the track(s) we're getting recommendations for
        for track in seed_track:
            if track in rec_tracks:
                rec_tracks.remove(track)
        return set(rec_tracks)

    def get_songs_per_artist(self, rec_track_tuples_list, max_tracks_per_artist=None):
        """
        combs tracks to remove any more than max_tracks_per_artistt per artist
        :param rec_track_tuples_list: list of tuples of track uris and their artist's uris
        :param max_tracks_per_artist: max number of tracks per artist in recommendations
        :return: a curated list of track uris
        """
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

    # extracts recommended tracks given a spotipy response
    def extract_rec_tracks(self, recs, max_tracks_per_artist=None):
        if not max_tracks_per_artist:
            rec_tracks = [track['uri'] for track in recs['tracks']]
        else:
            rec_tracks_tuples_list = self.extract_track_artist_tuples_list(recs)
            rec_tracks = self.get_songs_per_artist(rec_tracks_tuples_list, max_tracks_per_artist)
        return rec_tracks

    # given a spotipy response return a list of tuples of track uris and their artist's uris
    def extract_track_artist_tuples_list(self, recs):
        rec_tracks_tuples_list = [(track['uri'], track['artists'][0]['uri']) for track in recs['tracks']]
        return rec_tracks_tuples_list

    """
    Playlist stuff
    """

    def add_track_to_playlist(self, tracks, username, playlist_id):
        self.sp.user_playlist_add_tracks(username, playlist_id, tracks)

    # creates a playlist given a set of track uris
    def create_playlist(self, track_uris):
        playlist_id = self.sp.user_playlist_create(USERNAME, playlist_name, public=True)['id']

        chunk_size = 100
        for i in range(0, len(track_uris), chunk_size):
            chunk = list(track_uris)[i:i+chunk_size]
            print(f'Adding {len(chunk)} tracks to playlist {playlist_name}')
            self.add_track_to_playlist(tracks=chunk, username=USERNAME, playlist_id=playlist_id)

    def create_similar_playlist(self, playlist_id, max_recs_per_seed=5, max_tracks_per_artist=None):
        """
        creates a playlist with tracks similar to those in a given playlist's
        :param playlist_id: the id of the seed playlist
        :param max_recs_per_seed: max number of recommended tracks per song on seed playlist
        :param max_tracks_per_artist: max number of tracks per artist on target playlist
        """
        playlist = self.sp.user_playlist_tracks(USERNAME, playlist_id, limit=100)
        playlist_tracks = [item['track']['uri'] for item in playlist['items']]
        rec_tracks = set()
        tuples_list = []
        # for each track in the playlist, fetch up to a number of recommended tracks
        for track in playlist_tracks:
            seed_track = [track]
            # TODO register callback so filtering methtod isnt hardcoded
            track_features = self.sp.audio_features(seed_track)[0]
            all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
            targets = {f'target_{k}': v for k, v in all_track_stats.items()}

            recs = self.sp.recommendations(seed_tracks=seed_track, limit=max_recs_per_seed, **targets)
            if max_tracks_per_artist:
                # if max_tracks_per_artist specified, cache artist data too for later filtering
                track_artist_tuples_list = self.extract_track_artist_tuples_list(recs)
                tuples_list.extend(track_artist_tuples_list)
            else:
                # otherwise just add all thet track uris to the recommened list
                rec_uris = [track['uri'] for track in recs['tracks']]
                rec_tracks.update(rec_uris)
        if max_tracks_per_artist:
            # if max_tracks_per_artist specified, filter by given value
            rec_tracks.update(self.get_songs_per_artist(tuples_list, max_tracks_per_artist))
        # remove any tracks from original playlist as well. Doesn't always work for some reason (I blame spotify)
        for track in playlist_tracks:
            if track in rec_tracks:
                rec_tracks.remove(track)
        self.create_playlist(track_uris=rec_tracks)

    """
    Top Artists & Tracks
    """

    def get_top_tracks(self, track_limit=50, time_range='medium_term'):
        """
        gets the top up to 50 tracks for the user
        :param track_limit: number of tracks to fetch
        :param time_range: short_term, medium_term, or long_term
        :return: top track uris
        """
        top_tracks = self.sp.current_user_top_tracks(limit=track_limit, time_range=time_range)
        top_uris = [track['uri'] for track in top_tracks['items']]
        return top_uris

    def print_top_tracks(self, track_limit=50, time_range='medium_term'):
        top_tracks = self.sp.current_user_top_tracks(limit=track_limit, time_range=time_range)
        track_tuples = [(track['name'], track['artists'][0]['name']) for track in top_tracks['items']]
        x = 0
        for track_tuple in track_tuples:
            x += 1
            print('{:<5}{:<70}{}'.format(x, track_tuple[0], track_tuple[1]))

    def get_top_genres(self, artist_limit=50, time_range='medium_term'):
        """
        gets the user's most listened to artist's genres
        :param artist_limit: number of artists to fetch
        :param time_range: short_term, medium_term, or long_term
        :return: the list of artist's genres
        """
        top_artists = self.sp.current_user_top_artists(limit=artist_limit, time_range=time_range)
        genres = [artist['genres'] for artist in top_artists['items']]
        return genres

    def print_top_genres(self, artist_limit=50, time_range='medium_term'):
        top_artists = self.sp.current_user_top_artists(limit=artist_limit, time_range=time_range)
        artist_tuples = [(artist['name'], artist['genres']) for artist in top_artists['items']]
        x = 0
        for track_tuple in artist_tuples:
            x += 1
            print('{:<5}{:<50}{}'.format(x, track_tuple[0], track_tuple[1]))

    def get_average_user_track_data(self, top_uris):
        """
        collectts and averages the average-able attributes of the given tracks, buckets the non-average-able ones
        :param top_uris: top track uris
        :return: a tuple of the averages and the buckets
        """
        total_tracks = len(top_uris)
        average_map = {}
        top_map = {x: {} for x in non_divisible_attrs}
        track_features = self.sp.audio_features(tracks=top_uris)
        for feature_set in track_features:
            for key, val in feature_set.items():
                # track total
                if key in divisible_attrs:
                    if key in average_map:
                        average_map[key] = average_map[key] + val
                    else:
                        average_map[key] = val
                # track frequency
                elif key in non_divisible_attrs:
                    if top_map[key]:
                        if val in top_map[key]:
                            top_map[key][val] = top_map[key][val] + 1
                        else:
                            top_map[key].update({val: 1})
                    else:
                        top_map[key] = {val: 1}
        for key, val in average_map.items():
            average_map[key] = round(average_map[key]/total_tracks, 3)
        for key, val in top_map.items():
            top_map[key] = sorted(val, key=val.__getitem__, reverse=True)
        return average_map, top_map

    def rank_genres(self, genre_lists, top=5):
        """
        derives the most listened to genres given a list of lists of genres
        :param genre_lists: list of genres lists
        :param top: number of genres to return
        :return: the top genres
        """
        genre_map = {}
        for genre_list in genre_lists:
            for genre in genre_list:
                if genre in genre_map:
                    genre_map[genre] = genre_map[genre] + 1
                else:
                    genre_map[genre] = 1
        return sorted(genre_map, key=genre_map.__getitem__, reverse=True)[:top]

    # needs to be reworked; fringe music genres can tip the scales too heavily
    def create_average_top_playlist(self, top_genres, div_stats, non_div_stats, rec_limit=limit):
        """
        creates a playlist based on the average stats from a user's top artists/genres
        :param top_genres: most listened to genres
        :param div_stats: the features that have been averaged
        :param non_div_stats: the features that have been bucketed
        :param rec_limit: max number of recommendations per track, up to 100
        :return:
        """
        targets = {f'target_{k}': v for k, v in div_stats.items()}
        targets.update({f'target_{k}': v[0] for k, v in non_div_stats.items()})
        rec_tracks = set()
        print(top_genres)
        for genre in top_genres:
            print(genre)
            recs = self.sp.recommendations(seed_genres=[genre], limit=rec_limit, **targets)
            print(len(recs['tracks']))
            rec_uris = [track['uri'] for track in recs['tracks']]
            rec_tracks.update(rec_uris)
        # recs = self.sp.recommendations(seed_genres=top_genres, limit=rec_limit, **targets)
        print(f"Creating playlist {playlist_name} with {len(rec_tracks)} tracks")
        # rec_uris = [track['uri'] for track in recs['tracks']]
        self.create_playlist(rec_tracks)
