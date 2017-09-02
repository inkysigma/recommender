"""A module representing a collector of training data."""
from recommender.collector.music import Track
from typing import List, Dict
import spotipy
import uuid


class Collector:
    """A class for collecting training data from various sources"""

    def get_track_list(self, count: int = 1000, skip: int = 0) -> List[Track]:
        """Get a list of tracks to be recorded"""
        pass

    def get_track(self, title: str) -> Track:
        """Gets a specific track from the resource."""
        pass

    def get_categories(self) -> List[str]:
        """Gets a list of categories given by the resource."""
        pass

    def get_offset(self, categorey: str) -> int:
        """Get the offset of the number of songs in a categorey"""
        pass

    def get_categorey_offset(self, categorey: str):
        pass


class SpotifyCollector(Collector):
    """Collects song from Spotify"""

    def __init__(self, cid: str, csecret: str):
        """
        Create a SpotifyCollector with the parameters
        Args:
            cid (str): the client id. It is obtained from the Spotify Developer Console
            csecret (str): the client secret. It is obtained from the Spotify Developer Console
        """
        self.credential = spotipy.oauth2.SpotifyClientCredentials(
            client_id=cid,
            client_secret=csecret)
        self.spotify = spotipy.Spotify(
            client_credentials_manager=self.credential)
        self.__categories__ = []

    def get_categories(self) -> List[str]:
        """
        Get a list of categories from Spotify.
        Returns:
            List[str]: a list of categories that are available.
        """
        self.__categories__ = self.spotify.categories()["categories"]["items"]
        return self.__categories__

    def __get_genre__(self, track_id) -> List[str]:
        pass

    def get_track_list(self, count: int = 100, skip: int = 0) -> Dict[str, List[Track]]:
        """
        Get a list of tracks with the count of the list specified.
        Args:
            count (int): the number of tracks to get per categorey.
                Use get current_offset to get the offset as tracked by this collector.
                It is recommended to cache this result for later use.
        """
        if self.__categories__ is []:
            self.get_categories()
        tracks = {}
        for categorey in self.__categories__:
            playlist_id = categorey["id"]
            owner = categorey["owner"]
            owner_id = owner["id"]
            tracks = self.spotify.user_playlist(owner_id, playlist_id)["items"]
            tracks[categorey["id"]] = []
            for track in tracks:
                tracks[categorey["id"]].append(Track(
                    tid = track["track"]["id"],
                    url = track["track"]["href"],
                    title = track["track"]["name"]
                ))

        return tracks

    def get_track(self, title: str):
        pass
