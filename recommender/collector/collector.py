"""A module representing a collector of training data."""
from typing import List, Dict, Tuple, Callable, Any, Union
from recommender.collector.music import Track, Category
import spotipy
import spotipy.oauth2
import urllib.request
import urllib.response
import http.client
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
        """Get a list of possible genres"""
        pass

    def fetch_tracks(self, categories: List[Category], added: Callable[[str], bool], count: int = 100, skip: int = 0) \
            -> Dict[str, List[Track]]:
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
        """Get the category offset.
        Args:
            category (str): the category to consider
        """
        pass

    def fetch_track_sample(self, directory: str,
                           tracks: List[Track]) -> List[Tuple[Track, str]]:
        """
        Fetch the audio file track sample from the remote resource.
        Args:
            directory (str): the directory to download the samples into
            tracks (List[Track]): the list of tracks to download
        """
        pass

    def get_genre_name(self, gen: str) -> str:
        """"""
        pass


class SpotifyCollector(Collector):
    """
    A class for populating the track database with tracks from Spotify
    """

    def __init__(self, spotify_id: str, spotify_secret: str) -> None:
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
        self.__categories__: List[Dict[str, Any]] = []
        self.__genres__: List[str] = []

    def __get_genres__(self, track: Dict[str, Any]) -> List[str]:
        if not self.__genres__:
            self.get_genre_list()
        ids = []
        for artists in track["track"]["artists"]:
            ids.append(artists["id"])
        genres: List[str] = []
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
            if genre == gen:
                return genre
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

    def fetch_playlist(self, user: str, playlist_id: str, category: str,
                       added: Callable[[str], bool], skip: int = 0, count: int = 0) \
            -> Tuple[List[Track], int]:
        if not playlist_id:
            raise NotImplementedError
        download_count = 0
        tracks: List[Track] = []
        while download_count < count or count < 0:
            more_tracks = self.spotify.user_playlist_tracks(user, playlist_id, limit=min(count - download_count, 50),
                                                            offset=skip + download_count)

            for track in more_tracks["items"]["tracks"]:
                if not track["track"]["preview_url"] or added(
                        track["track"]["id"]):
                    continue
                fetched_track = Track(
                    track_id=track["track"]["id"],
                    title=track["track"]["name"],
                    url=track["track"]["preview_url"]
                )
                fetched_track.genre_list = self.__get_genres__(
                    track
                )
                fetched_track.category_list = [category]
                tracks.append(fetched_track)
                download_count = download_count + 1

            if download_count + \
                    skip == int(more_tracks["count"]) or skip > int(more_tracks["count"]):
                break

        return tracks, download_count

    def fetch_tracks(self, categories: List[Category], added: Callable[[
                     str], bool], count: int = 100, skip: int = 0) -> Dict[str, List[Track]]:
        """
        Fetch tracks from Spotify into a map of ids and tracks
        Args:
            categories (List[Category]): the list of category with both the category internal id and id filled
            added (Callable[[str], bool]): a test for whether a track is added
            count (int): the number of tracks to get per category.
                Use get current_offset to get the offset as tracked by this collector.
                It is recommended to cache this result for later use. Use a negative to indicate to download
                all tracks available.
            skip (int): the number of tracks to skip over.

        Returns:
            Dict[str, List[Track]]: a dictionary of internal ids and tracks
        """
        if not self.__categories__:
            self.get_category_list()
        tracks: Dict[str, List[Track]] = dict()

        for category in categories:
            playlists = self.spotify.category_playlists(
                category_id=category.category_id)["playlists"]

            tracks[category.cid] = []
            downloaded = 0
            for playlist in playlists:
                downloaded_tracks, count = self.fetch_playlist(playlist["owner"]["id"], playlist["id"], category.category_id,
                                                               added, skip, count - downloaded)
                tracks[category.cid].extend(downloaded_tracks)
                downloaded += count
                if downloaded >= count and count > 0:
                    break

        return tracks

    def fetch_track_sample(self, directory: str,
                           tracks: List[Track]) -> List[Tuple[Track, str]]:
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
            ext = mimetypes.guess_extension(response.getheader("content-type"))
            file_name = f"{os.path.join(directory,track.track_id)}{ext}"
            with open(file_name, "wb+") as track_file:
                chunk = response.read(chunk_size)
                while chunk:
                    track_file.write(chunk)
                    chunk = response.read(chunk_size)
            samples.append((track, file_name))

        return samples

    def get_category_offset(self, category: str) -> Dict[str, int]:
        pass

    def get_track(self, tid: str) -> Track:
        pass
