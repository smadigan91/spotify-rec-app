from typing import List


class TrackFeatures:

    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.duration_ms: int = values.get("duration_ms", 0)
        self.key: int = values.get("key", 0)
        self.mode: int = values.get("mode", 0)
        self.time_signature: int = values.get("time_signature", 0)
        self.acousticness: float = values.get("acousticness", 0)
        self.danceability: float = values.get("danceability", 0)
        self.energy: float = values.get("energy", 0)
        self.instrumentalness: float = values.get("instrumentalness", 0)
        self.liveness: float = values.get("liveness", 0)
        self.loudness: float = values.get("loudness", 0)
        self.speechiness: float = values.get("speechiness", 0)
        self.valence: float = values.get("valence", 0)
        self.tempo: float = values.get("tempo", 0)
        self.id: str = values.get("id", '')
        self.uri: str = values.get("uri", '')
        self.track_href: str = values.get("track_href", '')
        self.analysis_url: str = values.get("analysis_url", '')
        self.type: str = values.get("type", '')


class Track:

    class ArtistList(list):

        class Artist:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.href: str = values.get("href", '')
                self.id: str = values.get("id", '')
                self.name: str = values.get("name", '')
                self.type: str = values.get("type", '')
                self.uri: str = values.get("uri", '')

        def __init__(self, values: list = None):
            super().__init__()
            values = values if values is not None else []
            self[:] = [self.Artist(value) for value in values]

    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.artists = self.ArtistList(values=values.get("artists"))
        self.disc_number: int = values.get("disc_number", 0)
        self.duration_ms: int = values.get("duration_ms", 0)
        self.explicit: bool = values.get("explicit", False)
        self.href: str = values.get("href", '')
        self.id: str = values.get("id", '')
        self.is_playable: bool = values.get("is_playable", False)
        self.name: str = values.get("name", '')
        self.preview_url: str = values.get("preview_url", '')
        self.track_number: int = values.get("track_number", 0)
        self.type: str = values.get("type", '')
        self.uri: str = values.get("uri", '')


class Artist:

    class Followers:

        def __init__(self, values: dict = None):
            values = values if values is not None else {}
            self.total: int = values.get("total", 0)

    class Images(list):

        class Items:

            def __init__(self, values: dict = None):
                values = values if values is not None else {}
                self.height: int = values.get("height", 0)
                self.url: str = values.get("url", '')
                self.width: int = values.get("width", 0)

        def __init__(self, values: list = None):
            super().__init__()
            values = values if values is not None else []
            self[:] = [self.Items(value) for value in values]

    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.followers = self.Followers(values=values.get("followers"))
        self.genres: List[str] = values.get("genres", [])
        self.href: str = values.get("href", '')
        self.id: str = values.get("id", '')
        self.images = self.Images(values=values.get("images"))
        self.name: str = values.get("name", '')
        self.popularity: int = values.get("popularity", 0)
        self.type: str = values.get("type", '')
        self.uri: str = values.get("uri", '')
