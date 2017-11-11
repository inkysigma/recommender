"""A module representing a collector of training data."""
from recommender.collector.music import Track, Category
from typing import List, Dict, Tuple, Callable
import spotipy
import spotipy.oauth2
import urllib.request
import mimetypes
import os
import urllib.parse


class Collector:
    """
    A class for collecting tracks from various sources
    """

    def get_category_list(self) -> List[str]:
        """Gets a list of categories given by the resource."""
        pass

    def get_category_name(self, cat: str):
        """Get the category name based on the category id"""
        pass

    def get_genre_list(self) -> List[str]:
        pass

    def fetch_tracks(self, categories: List[str], added: Callable[[str], bool], count: int = 100, skip: int = 0) -> \
            List[Track]:
        """
        Get a list of tracks with the count of the list specified.
        Args:
            categories (List[str]): the list of category ids used by the remote server
            added (Callable[[str], bool]): a function to determine whether a track has been added based on its id
            count (int): the number of tracks to get per category.
                Use get current_offset to get the offset as tracked by this collector.
                It is recommended to cache this result for later use.
            skip (int): the number of tracks to skip over.
        """
        pass

    def get_offset(self, category: str) -> int:
        """Get the offset of the number of songs in a categorey"""
        pass

    def get_track(self, tid: str) -> Track:
        """
        Gets a track based on a specified id.
        Args:
            tid (str): the track to be added

        Returns:
            Track: a track as represented by the remote resource.
        """
        pass

    def get_category_offset(self, category: str) -> Dict[str, int]:
        pass

    def fetch_track_sample(self, directory: str, track: List[Track]) -> List[Tuple[Track, str]]:
        pass

    def get_genre_name(self, gen: str) -> str:
        pass


class SpotifyCollector(Collector):
    """
    A class for populating the track database with tracks from Spotify
    """

    def __init__(self, spotify_id: str, spotify_secret: str):
        """
        Create a SpotifyCollector with the parameters
        Args:
            spotify_id (str): the client id. It is obtained from the Spotify Developer Console
            spotify_secret (str): the client secret. It is obtained from the Spotify Developer Console
        """
        self.credential = spotipy.oauth2.SpotifyClientCredentials(
            client_id=spotify_id,
            client_secret=spotify_secret
        )
        self.spotify = spotipy.Spotify(
            client_credentials_manager=self.credential
        )
        self.__categories__ = []
        self.__genres__ = []

    def __get_genres__(self, track: object) -> List[str]:
        if not self.__genres__:
            self.get_genre_list()
        ids = []
        for artists in track["track"]["artists"]:
            ids.append(artists["id"])
        genres = []
        artists = self.spotify.artists(ids)["artists"]
        for artist in artists:
            genres.extend(
                set([g for genre in artist["genres"] for g in genre.split()]).intersection(set(self.__genres__)))
        return genres

    def get_genre_list(self) -> List[str]:
        if self.__genres__:
            return self.__genres__
        self.__genres__ = self.spotify.recommendation_genre_seeds()["genres"]
        return self.__genres__

    def get_genre_name(self, gen: str) -> str:
        if not self.__genres__:
            self.get_genre_list()
        for genre in self.__genres__:
            if genre["id"] == gen:
                return genre["name"]
        return ""

    def get_category_list(self) -> List[str]:
        """
        Get a list of categories from Spotify.
        Returns:
            List[str]: a list of categories that are available with their ids as strings.
        """
        if not self.__categories__:
            self.__categories__ = []
            count = 0
            categories = self.spotify.categories()
            while count < categories["categories"]["total"]:
                self.__categories__.extend(categories["categories"]["items"])
                count += len(categories["categories"]["items"])
                categories = self.spotify.categories(limit=20, offset=count)
        return [category["id"] for category in self.__categories__]

    def get_category_name(self, cat: str) -> str:
        """
        Gets the name of a category based on an id
        Args:
            cat: the id of the category as given by the resource.

        Returns:
            str: the name of the category
        """
        if not self.__categories__:
            self.get_category_list()
        for category in self.__categories__:
            if category["id"] == cat:
                return category["name"]
        return ""

    def fetch_tracks(self, categories: List[Category], added: Callable[[str], bool], count: int = 100, skip: int = 0,
                     download_all: bool = False) -> Dict[str, List[Track]]:
        """
        Fetch tracks from Spotify into a map of ids and tracks
        Args:
            categories (List[Category]): the list of category with both the category internal id and id filled
            added (Callable[[str], bool]): a test for whether a track is added
            count (int): the number of tracks to get per category.
                Use get current_offset to get the offset as tracked by this collector.
                It is recommended to cache this result for later use.
            skip (int): the number of tracks to skip over.
            download_all (bool): whether all tracks should be downloaded

        Returns:
            Dict[str, List[Track]]: a dictionary of internal ids and tracks
        """
        if not self.__categories__:
            self.get_category_list()
        tracks = dict()

        track_count = 0
        skip_count = 0

        for category in categories:
            playlists = self.spotify.category_playlists(category_id=category.category_id)["playlists"]

            for playlist in playlists["items"]:
                owner = playlist["owner"]
                owner_id = owner["id"]
                while track_count < count and not download_all:
                    remote = self.spotify.user_playlist_tracks(owner_id, playlist["id"], offset=track_count)

                    # Skip the playlist if we are going to skip over it
                    if skip_count < skip and skip_count + remote["total"] < skip:
                        skip_count += remote["total"]
                        continue

                    tracks[category.cid] = []
                    for index, track in enumerate(remote["items"]["tracks"], start=skip - skip_count):
                        if track["track"]["preview_url"] is None or added(track["track"]["id"]):
                            continue
                        t = Track(
                            track_id=track["track"]["id"],
                            title=track["track"]["name"],
                            url=track["track"]["preview_url"]
                        )
                        t.genre_list = self.__get_genres__(track)
                        t.category_list = [category.category]
                        tracks[category.cid].append(t)
                        track_count = track_count + 1

                        if track_count >= count:
                            break
                    if track_count == remote["count"]:
                        break
                track_count = 0
                skip_count = 0

        return tracks

    def fetch_track_sample(self, directory: str, tracks: List[Track]) -> List[Tuple[Track, str]]:
        """
        Download track samples for the tracks
        Args:
            directory (str): the directory to download to
            tracks (List[Track]): a list of tracks to download

        Returns:
            List[str]: a list of strings representing the files downloaded in the order given
        """
        samples = []
        chunk_size = 16 * 1024

        if not os.path.exists(directory):
            os.makedirs(directory)

        for track in tracks:
            response = urllib.request.urlopen(track.url.decode("ASCII"))
            ext = mimetypes.guess_extension(response.headers["content-type"])
            file_name = f"{os.path.join(directory,track.track_id)}{ext}"
            with open(file_name, "wb+") as f:
                chunk = response.read(chunk_size)
                while chunk:
                    f.write(chunk)
                    chunk = response.read(chunk_size)
            samples.append((track, file_name))

        return samples

    def get_category_offset(self, category: str) -> Dict[str, int]:
        pass

    def get_track(self, tid: str) -> Track:
        pass
