"""A module representing a collector of training data."""
from recommender.collector.music import Track
from typing import List, Dict, Tuple
import spotipy
import spotipy.oauth2
import numpy as np
import urllib.request
import mimetypes
import librosa
import os
import urllib.parse


class Collector:
    """A class for collecting training data from various sources"""

    def get_category_list(self) -> List[str]:
        """Gets a list of categories given by the resource."""
        pass

    def get_genre_list(self) -> List[str]:
        pass

    def get_track_list(self, count: int = 1000, skip: int = 0) -> List[Track]:
        """
        Get a list of tracks with the count of the list specified.
        Args:
            count (int): the number of tracks to get per categorey.
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

    def fetch_track_sample(self, track: List[Track]) -> List[Tuple[np.array, List[int]]]:
        pass


class SpotifyCollector(Collector):
    """Collects song from Spotify"""

    def __init__(self, cid: str, csecret: str, tempdir: str):
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
        self.__genres__ = []
        self.__tempdir__ = tempdir
        if not os.path.exists(self.__tempdir__):
            os.makedirs(self.__tempdir__)

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

    def get_track_list(self, count: int = 100, skip: int = 0) -> Dict[str, List[Track]]:
        if not self.__categories__:
            self.get_category_list()
        tracks = {}

        list_count = 0
        skip_count = 0
        for category in self.__categories__:
            playlists = self.spotify.category_playlists(category_id=category["id"])["playlists"]
            for playlist in playlists["items"]:
                owner = playlist["owner"]
                owner_id = owner["id"]
                remote = self.spotify.user_playlist_tracks(owner_id, playlist["id"])

                # Skip the playlist if we have already covered it
                if skip_count < skip and skip_count + remote["total"] < skip:
                    skip_count += remote["total"]
                    continue

                tracks[category["id"]] = []
                for index, track in enumerate(remote["items"], start=skip - skip_count):
                    t = Track(
                        track_id=track["track"]["id"],
                        title=track["track"]["name"],
                        url=track["track"]["preview_url"]
                    )
                    if t.url is None:
                        continue
                    t.genre_list = self.__get_genres__(track)
                    t.category_list = [category["name"]]
                    tracks[category["id"]].append(t)
                    list_count += 1
                    if list_count >= count:
                        break
                if list_count >= count:
                    list_count = 0
                    skip_count = 0
                    break

        return tracks

    def fetch_track_sample(self, tracks: List[Track]) -> List[Tuple[Track, str]]:
        """
        Download track samples for the tracks
        Args:
            tracks (List[Track]): a list of tracks to download

        Returns:
            List[str]: a list of strings representing the files downloaded in the order given
        """
        samples = []
        chunk_size = 16 * 1024
        for track in tracks:
            response = urllib.request.urlopen(track.url.decode("ASCII"))
            ext = mimetypes.guess_extension(response.headers["content-type"])
            file_name = f"{os.path.join(self.__tempdir__,track.track_id)}{ext}"
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
