import spotipy
import inspect
key_attrs = ['energy', 'valence', 'danceability']
other_attrs = ['key', 'mode', 'tempo']# 'time_signature', 'acousticness', 'instrumentalness', 'speechiness']
default_playlist_name = "playlist_name"
default_rec_limit = 15


class SpotipyWrapper:

    sp: spotipy.Spotify = None

    def __init__(self, user, access_token):
        self.user = user
        self.sp = spotipy.Spotify(auth=access_token)

    def get_targeted_recs(self, seed_track, rec_limit=default_rec_limit, max_tracks_per_artist=None,
                          target_popularity=False, min_popularity=False, max_popularity=False, popularity_scalar=1,
                          min_popularity_override=None, max_popularity_override=None):
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
        if target_popularity:
            track = self.sp.track(track_id=track_features['id'])
            popularity = track['popularity']
            name = track['name']
            popularity = float(popularity*popularity_scalar)
            if popularity > 100:
                print(f'popularity was over 100 ({popularity}) defaulting to 100')
                popularity = 100
            elif popularity < 1:
                print(f'popularity was under 1 ({popularity}) defaulting to 1')
                popularity = 1
            if min_popularity:
                if min_popularity_override:
                    targets['min_popularity'] = int(round(min_popularity_override))
                else:
                    targets['min_popularity'] = int(round(popularity))
                    print(f'min_popularity = {popularity} for {name}')
            elif max_popularity:
                if max_popularity_override:
                    targets['max_popularity'] = int(round(max_popularity_override))
                else:
                    targets['max_popularity'] = int(round(popularity))
                    print(f'max_popularity = {popularity} for {name}')
            else:
                targets['target_popularity'] = int(round(popularity))
                print(f'target_popularity = {popularity} for {name}')
        recs = self.sp.recommendations(seed_tracks=seed_track, limit=rec_limit, **targets)
        if inspect.stack()[1][3] == 'create_similar_playlist':
            return recs
        else:
            rec_tracks = self.extract_rec_tracks(recs, max_tracks_per_artist)
            # remove the track(s) we're getting recommendations for
            for track in seed_track:
                if track in rec_tracks:
                    rec_tracks.remove(track)
            return set(rec_tracks)

    def get_mixed_recs(self, seed_track, variance, rec_limit=default_rec_limit, max_tracks_per_artist=None):
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

    def get_fuzzy_recs(self, seed_track, variance, rec_limit=default_rec_limit, max_tracks_per_artist=None):
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

    def get_recursive_recs(self, seed_tracks, max_recs_per_seed=5, depth=1, totals=None):
        if not totals:
            totals = set()
        while depth > 0:
            recs = set()
            for track in seed_tracks:
                track_recs = self.get_targeted_recs(seed_track=[track], rec_limit=max_recs_per_seed)
                recs.update(track_recs)
            totals.update(recs)
            depth = depth - 1
            self.get_recursive_recs(seed_tracks=recs, max_recs_per_seed=max_recs_per_seed, depth=depth, totals=totals)
        return totals

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

    def create_playlist(self, track_uris, playlist_name=default_playlist_name):
        playlist_id = self.sp.user_playlist_create(self.user, playlist_name, public=True)['id']
        chunk_size = 100
        for i in range(0, len(track_uris), chunk_size):
            chunk = list(track_uris)[i:i+chunk_size]
            print(f'Adding {len(chunk)} tracks to playlist {playlist_name}')
            self.add_track_to_playlist(tracks=chunk, username=self.user, playlist_id=playlist_id)

    def get_playlist_tracks(self, playlist_id, track_limit=None):
        track_uris = set()
        playlist = self.sp.user_playlist_tracks(self.user, playlist_id,
                                                limit=track_limit if track_limit and track_limit <= 100 else 100)
        track_uris.update(item['track']['uri'] for item in playlist['items'])
        offset = 0
        while playlist['next'] and (track_limit is None or track_limit != len(track_uris)):
            limit = track_limit - len(track_uris) if track_limit else 100
            offset = offset + 100
            playlist = self.sp.user_playlist_tracks(self.user, playlist_id,
                                                    limit=limit if limit <= 100 else 100, offset=offset)
            track_uris.update(item['track']['uri'] for item in playlist['items'])
        return track_uris

    def create_similar_playlist(self, playlist_id, max_recs_per_seed=5, max_tracks_per_artist=None, track_limit=None,
                                playlist_name=None, rec_func=None, **kwargs):
        """
        creates a playlist with tracks similar to those in a given playlist's
        :param playlist_id: the id of the seed playlist
        :param max_recs_per_seed: max number of recommended tracks per song on seed playlist
        :param max_tracks_per_artist: max number of tracks per artist on target playlist
        :param track_limit: number of tracks from the given playlist to fetch recommendations for
        """
        playlist_tracks = self.get_playlist_tracks(playlist_id=playlist_id, track_limit=track_limit)
        rec_tracks = set()
        tuples_list = []
        # for each track in the playlist, fetch up to a number of recommended tracks
        for track in playlist_tracks:
            seed_track = [track]
            # TODO register callback so filtering methtod isnt hardcoded
            if not rec_func:
                track_features = self.sp.audio_features(seed_track)[0]
                all_track_stats = {k: v for k, v in track_features.items() if (k in key_attrs or k in other_attrs)}
                targets = {f'target_{k}': v for k, v in all_track_stats.items()}
                recs = self.sp.recommendations(seed_tracks=seed_track, limit=max_recs_per_seed, **targets)
            else:
                recs = rec_func(seed_track, rec_limit=max_recs_per_seed, max_tracks_per_artist=max_tracks_per_artist,
                                **kwargs)
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
        self.create_playlist(track_uris=rec_tracks, playlist_name=playlist_name)

    def create_radio_playlist(self, seed_tracks, max_recs_per_seed=5, depth=1):
        track = self.sp.track(seed_tracks[0])
        track_title = track['name']
        playlist_title = f"{track_title if len(seed_tracks) == 1 else track_title + ' etc.'} Radio"
        recs = self.get_recursive_recs(seed_tracks=seed_tracks, max_recs_per_seed=max_recs_per_seed, depth=depth)
        self.create_playlist(recs, playlist_title)

    """
    Top Artists & Tracks
    """
    def get_top_recs(self, track_limit=50, time_range='short_term', max_recs_per_seed=5, max_tracks_per_artist=None):
        # gets the top up to max_recs_per_seed recommendations for each of a user's top recent songs
        top_tracks = self.get_top_tracks(track_limit, time_range)
        rec_tracks = set()
        for track in top_tracks:
            rec_tracks.update(self.get_targeted_recs(seed_track=[track], rec_limit=max_recs_per_seed,
                                                     max_tracks_per_artist=max_tracks_per_artist))
        return rec_tracks

    def get_top_tracks(self, track_limit=50, time_range='medium_term'):
        """
        gets the top up to 50 tracks for the user
        :param track_limit: number of tracks to fetch
        :param time_range: short_term, medium_term, or long_term
        :return: top track uris
        """
        top_uris = set()
        for i in range(0, track_limit, 50):
            top_tracks = self.sp.current_user_top_tracks(offset=i, limit=track_limit, time_range=time_range)
            top_uris.update(track['uri'] for track in top_tracks['items'])
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
