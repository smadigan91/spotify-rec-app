import spotipy
import time
from .models import *
from typing import Set
from spotipy.client import SpotifyException

MAX_PLAYLIST_SIZE = 10000


class SpotifyWrapperException(Exception):

    def __init(self, message):
        super(SpotifyWrapperException, self).__init__(message)

    @property
    def message(self):
        return self.message


class SpotifyWrapper:

    def __init__(self, access_token, logger):
        self.sp = spotipy.Spotify(auth=access_token)
        self.username = self.sp.me()['id']
        self.log = logger
        self.filter_map = {}

    def get_playlist_tracks(self, playlist_id, track_limit=None):
        tracks = set()
        playlist_info = self.sp.playlist(playlist_id)
        playlist_name = playlist_info['name']
        playlist = self.sp.playlist_tracks(playlist_id,
                                           limit=track_limit if track_limit and track_limit <= 100 else 100)
        tracks.update(Track(item['track']) for item in playlist['items'])
        offset = 0
        while playlist['next'] and (track_limit is None or track_limit != len(tracks)):
            limit = track_limit - len(tracks) if track_limit else 100
            offset = offset + 100
            playlist = self.sp.playlist_tracks(playlist_id, limit=limit if limit <= 100 else 100, offset=offset)
            tracks.update(Track(item['track']) for item in playlist['items'])
        self.log.info(f"Retrieved {len(tracks)} tracks for playlist {playlist_name}")
        return playlist_name, tracks

    @staticmethod
    def get_recommendation_filters(filters: RecSpec.Filters):
        filter_map = {}
        target_attributes_dict = filters.target.track_attributes.as_dict()
        min_attributes_dict = filters.min.track_attributes.as_dict()
        max_attributes_dict = filters.max.track_attributes.as_dict()
        for track_attribute, value in target_attributes_dict.items():
            if value is not None:
                filter_map[f'target_{track_attribute}'] = value
        for track_attribute, value in min_attributes_dict.items():
            if value is not None and not target_attributes_dict.get(track_attribute):
                filter_map[f'min_{track_attribute}'] = value
        for track_attribute, value in max_attributes_dict.items():
            if value is not None and not target_attributes_dict.get(track_attribute):
                filter_map[f'max_{track_attribute}'] = value
        return filter_map

    def apply_custom_filters(self, rec_tracks: Set[Track], custom_filters: RecSpec.Filters.Custom):

        def filter_max_tracks_per_artist(max_tracks_per_artist):
            track_set = set()
            if max_tracks_per_artist:
                artist_track_map = {}
                for track in rec_tracks:
                    artist_name = track.artist_name
                    artist_tracks = artist_track_map.get(artist_name)
                    if not artist_tracks:
                        artist_track_map[artist_name] = [track]
                        track_set.add(track)
                    else:
                        if len(artist_tracks) < max_tracks_per_artist:
                            artist_track_map[artist_name].append(track)
                            track_set.add(track)
                return track_set
            else:
                return rec_tracks

        if custom_filters.max_tracks_per_artist:
            rec_size_before = len(rec_tracks)
            self.log.info(f"Filtering recommendations to {custom_filters.max_tracks_per_artist} "
                          "tracks per artist maximum")
            rec_tracks = filter_max_tracks_per_artist(custom_filters.max_tracks_per_artist)
            self.log.info(f"Filtering by max tracks per artist filtered out {rec_size_before - len(rec_tracks)} tracks")
        return rec_tracks

    def get_default_recommendations(self, filter_map, seed: RecSpec.Seed):
        rec_tracks = set()
        limit = seed.rec_limit
        self.log.info(f"Generating recommendations for {len(seed.genres)} seed genres, {len(seed.artists)} "
                      f"seed artists, and {len(seed.tracks)} seed tracks")
        if limit:
            self.log.info(f"Limiting recommendation playlist size to {limit} tracks")
        recommendations = self.sp.recommendations(seed_genres=seed.genres, seed_artists=seed.artists,
                                                  seed_tracks=seed.tracks, limit=limit, **filter_map)
        for rec_track in recommendations.get('tracks', []):
            # only add recommendations that didnt appear in the seed tracks
            if rec_track not in seed.tracks:
                rec_tracks.add(Track(rec_track))
        return rec_tracks

    def get_playlist_recommendations(self, filter_map, seed: RecSpec.Seed):
        rec_tracks = set()
        limit = seed.rec_limit
        playlist_name, playlist_tracks = self.get_playlist_tracks(playlist_id=seed.playlist)
        # keep track of songs in the original playlist - we dont want them showing up in the recommendations
        playlist_track_set = set()
        for playlist_track in playlist_tracks:
            playlist_track_set.add(playlist_track.effective_name)
        self.log.info(f"Generating recommendations for playlist {playlist_name} ({len(playlist_tracks)} tracks) "
                      f"with {len(seed.genres)} seed genres, {len(seed.artists)} seed artists, and "
                      f"{len(seed.tracks)} seed tracks")
        if limit:
            self.log.info(f"Limiting recommendations to {limit} tracks per track in {playlist_name}, for a maximum"
                          f"recommendation size of {limit * len(playlist_tracks)}")
        for track in playlist_tracks:
            recommendations = self.sp.recommendations(seed_genres=seed.genres, seed_artists=seed.artists,
                                                      seed_tracks=[track.id], limit=limit, **filter_map)
            for track_to_add in recommendations.get('tracks', []):
                rec_track = Track(track_to_add)
                # only add tracks whose (name + artist name) is not present in the seed playlist
                if rec_track.effective_name not in playlist_track_set:
                    rec_tracks.add(rec_track)
                    playlist_track_set.add(rec_track.effective_name)
        return rec_tracks

    def get_recommended_tracks(self, rec_spec: RecSpec):
        seed = rec_spec.seed
        self.filter_map = self.get_recommendation_filters(rec_spec.filters)
        self.log.info(f'Filters are: {self.filter_map}')
        if not seed.playlist:
            rec_tracks = self.get_default_recommendations(filter_map=self.filter_map, seed=seed)
        else:
            rec_tracks = self.get_playlist_recommendations(filter_map=self.filter_map, seed=seed)
        if rec_tracks:
            total_recs = len(rec_tracks)
            rec_tracks = self.apply_custom_filters(rec_tracks=rec_tracks, custom_filters=rec_spec.filters.custom)
            self.log.info(f"Retrieved {total_recs} recommendations")
            if total_recs > MAX_PLAYLIST_SIZE:
                raise SpotifyWrapperException('Generated more recommendations than the maximum playlist size will allow')
        return rec_tracks

    def create_playlist(self, tracks, playlist_name, seed: RecSpec.Seed):
        playlist_description = self.get_playlist_description(seed)
        playlist_id = self.create_playlist_with_retries(user=self.username, playlist_name=playlist_name,
                                                        playlist_description=playlist_description)
        chunk_size = 100
        for i in range(0, len(tracks), chunk_size):
            chunk = list(tracks)[i:i + chunk_size]
            self.log.info(f'Adding {len(chunk)} tracks to playlist {playlist_name}')
            self.add_tracks_to_playlist_with_retries(user=self.username, playlist_id=playlist_id, tracks=chunk)

    def generate_recommendations(self, rec_spec: RecSpec):
        rec_tracks = self.get_recommended_tracks(rec_spec)
        rec_track_ids = [rec_track.id for rec_track in rec_tracks]
        self.create_playlist(rec_track_ids, rec_spec.playlist_name, rec_spec.seed)

    def get_playlist_description(self, seed: RecSpec.Seed):
        sorted_keys = sorted(self.filter_map.keys())
        seeds = ""
        if seed.playlist:
            seeds = f"seed playlist: {seed.playlist}, "
        if seed.tracks:
            seeds += f"seed tracks: ({', '.join(track for track in seed.tracks)}), "
        if seed.artists:
            seeds += f"seed artists: ({', '.join(artist for artist in seed.artists)}), "
        if seed.genres:
            seeds += f"seed genres: ({', '.join(genre for genre in seed.genres)}), "
        attributes = ", ".join([f'{sorted_key}: ' + str(self.filter_map[sorted_key]) for sorted_key in sorted_keys if
                                self.filter_map.get(sorted_key) is not None])
        description = f"{seeds} {attributes}"
        self.log.info(f"Description: {description}")
        if len(description) > 300:
            self.log.info("Description was over 300 characters, defaulting to default playlist description")
            description = "Generated by spotify-rec-app"
        return description

    def create_playlist_with_retries(self, user, playlist_name, playlist_description, delay=0):
        try:
            playlist_id = self.sp.user_playlist_create(user=user, name=playlist_name,
                                                       description=playlist_description,
                                                       public=False)['id']
        except SpotifyException as spex:
            if spex.http_status == 429:
                delay += 1
                sleep_seconds = int(
                    spex.headers.get("Retry-After", delay)
                )
                self.log.info(f"Received a 429 while attempting to create playlist, retrying in {str(sleep_seconds)} "
                              f"seconds")
                time.sleep(sleep_seconds + 1)
                # try again after the wait period
                playlist_id = self.create_playlist_with_retries(user=user, playlist_name=playlist_name,
                                                                playlist_description=playlist_description, delay=delay)
            else:
                raise
        return playlist_id

    def add_tracks_to_playlist_with_retries(self, user, playlist_id, tracks, delay=0):
        try:
            self.sp.user_playlist_add_tracks(user=user, playlist_id=playlist_id, tracks=tracks)
        except SpotifyException as spex:
            if spex.http_status == 429:
                delay += 1
                sleep_seconds = int(
                    spex.headers.get("Retry-After", delay)
                )
                self.log.info(f"Received a 429 while attempting to create playlist, retrying in {str(sleep_seconds)} "
                              f"seconds")
                time.sleep(sleep_seconds + 1)
                # try again after the wait period
                self.add_tracks_to_playlist_with_retries(user=user, playlist_id=playlist_id, tracks=tracks, delay=delay)
            else:
                raise

