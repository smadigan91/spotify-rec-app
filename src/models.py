from typing import List


class ModelValidationException(Exception):

    def __init(self, message):
        self.__message = message
        super(ModelValidationException, self).__init__(message)

    @property
    def message(self):
        return self.__message


class Track:
    """
    Response from Spotify's Tracks API
    """
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.artists = self.ArtistList(values=values.get("artists"))
        self.artist_name = self.artists[0].name if self.artists else None
        self.disc_number: int = values.get("disc_number")
        self.duration_ms: int = values.get("duration_ms")
        self.explicit: bool = values.get("explicit", False)
        self.href: str = values.get("href", '')
        self.id: str = values.get("id", '')
        self.is_playable: bool = values.get("is_playable", False)
        self.name: str = values.get("name", '')
        self.preview_url: str = values.get("preview_url", '')
        self.track_number: int = values.get("track_number", 0)
        self.type: str = values.get("type", '')
        self.uri: str = values.get("uri", '')
        self.effective_name = self.name.lower() + self.artist_name.lower()

    def as_dict(self):
        return self.__dict__

    class ArtistList(list):

        def __init__(self, values: list = None):
            super().__init__()
            values = values if values is not None else []
            self[:] = [self.TrackArtist(value) for value in values]

        def as_dict(self):
            return self.__dict__

        class TrackArtist:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.href: str = values.get("href", '')
                self.id: str = values.get("id", '')
                self.name: str = values.get("name", '')
                self.type: str = values.get("type", '')
                self.uri: str = values.get("uri", '')

            def as_dict(self):
                return self.__dict__


class Artist:
    """
    Response from Spotify's Artists API
    """
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.genres: List[str] = values.get("genres", [])
        self.href: str = values.get("href", '')
        self.id: str = values.get("id", '')
        self.images = self.ImageList(values=values.get("images"))
        self.name: str = values.get("name", '')
        self.popularity: int = values.get("popularity", 0)
        self.type: str = values.get("type", '')
        self.uri: str = values.get("uri", '')

    def as_dict(self):
        return self.__dict__

    class ImageList(list):

        def __init__(self, values: list = None):
            super().__init__()
            values = values if values is not None else []
            self[:] = [self.Image(value) for value in values]

        def as_dict(self):
            return self.__dict__

        class Image:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.height: int = values.get("height", 0)
                self.url: str = values.get("url", '')
                self.width: int = values.get("width", 0)

            def as_dict(self):
                return self.__dict__


class TrackAttributes:
    """
    Every track attribute that can be tuned for custom recommendations
    """
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.duration_ms: int = values.get("duration_ms", None)
        self.key: int = values.get("key", None)
        self.mode: int = values.get("mode", None)
        self.acousticness: float = values.get("acousticness", None)
        self.danceability: float = values.get("danceability", None)
        self.energy: float = values.get("energy", None)
        self.instrumentalness: float = values.get("instrumentalness", None)
        self.liveness: float = values.get("liveness", None)
        self.speechiness: float = values.get("speechiness", None)
        self.valence: float = values.get("valence", None)
        self.tempo: float = values.get("tempo", None)
        self.popularity: int = values.get("popularity", None)

    def as_dict(self):
        return self.__dict__


class TrackAudioFeatures:
    """
    Response from Spotify's Audio Features API
    """
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.track_attributes = TrackAttributes(values)
        self.id: str = values.get("id", '')
        self.uri: str = values.get("uri", '')
        self.track_href: str = values.get("track_href", '')
        self.analysis_url: str = values.get("analysis_url", '')
        self.type: str = values.get("type", '')

    def as_dict(self):
        return self.__dict__


class RecSpec:
    """
    Short for recommendation specification hehe
    """
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.playlist_name = values.get('playlist_name')
        if not self.playlist_name:
            self.playlist_name = "generated playlist"
        self.seed = self.Seed(values=values.get("seed"))
        self.filters = self.Filters(values=values.get("filters"))

    def as_dict(self):
        return self.__dict__

    class Seed:

        def __init__(self, values: dict = None):
            values = values if values is not None else {}
            self.rec_limit = values.get('recommendation_limit', 100)
            if not self.rec_limit:
                self.rec_limit = 100
            self.playlist: str = extract_resource_id(values.get("playlist", None))
            self.tracks: List[str] = list() if not values.get("tracks") else \
                [extract_resource_id(track) for track in values.get("tracks")]
            self.artists: List[str] = list() if not values.get("artists") else \
                [extract_resource_id(artist) for artist in values.get("artists", [])]
            self.genres: List[str] = list() if not values.get("genres") else values.get("genres")
            self.validate()

        def validate(self):
            if len(self.tracks) + len(self.artists) + len(self.genres) > 5:
                raise ModelValidationException("There can only be 5 total combined seed tracks, artists, and genres")

        def as_dict(self):
            return self.__dict__

    class Filters:

        def __init__(self, values: dict = None):
            values = values if values is not None else {}
            self.target = self.Target(values=values.get("target"))
            self.min = self.Min(values=values.get("min"))
            self.max = self.Max(values=values.get("max"))
            self.custom = self.Custom(values=values.get("custom"))

        def as_dict(self):
            return self.__dict__

        class Target:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.track_attributes = TrackAttributes(values=values.get("track_attributes"))

            def as_dict(self):
                return self.__dict__

        class Min:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.track_attributes = TrackAttributes(values=values.get("track_attributes"))

            def as_dict(self):
                return self.__dict__

        class Max:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.track_attributes = TrackAttributes(values=values.get("track_attributes"))

            def as_dict(self):
                return self.__dict__

        class Custom:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.max_tracks_per_artist = values.get("max_tracks_per_artist")

            def as_dict(self):
                return self.__dict__


def extract_resource_id(resource_uri):
    resource_id = resource_uri
    if resource_id:
        if "open.spotify.com" in resource_uri:
            resource_id = resource_uri.split('/')[-1].split('?')[0]
        if 'spotify:' in resource_uri:
            resource_id = resource_uri.split(':')[2]
        if 'api.spotify.com' in resource_uri:
            resource_id = resource_uri.split('/')[-1]
    return resource_id
