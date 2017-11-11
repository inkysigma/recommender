from recommender.collector.collector import SpotifyCollector
from recommender.collector.music import Track
import unittest
import configparser
import json
import os
import os.path


class SpotifyCollectorTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("test.ini") and not os.path.exists("../test.ini"):
            print("File test.ini not found")
            print(f"Current directory is: {os.path.dirname(os.path.abspath(__file__))}")
        config = configparser.ConfigParser()
        config.read("test.ini")
        if not os.path.exists("test.ini"):
            config.read("../test.ini")
        self.collector = SpotifyCollector(config.get("spotify", "client_id"), config.get("spotify", "client_secret"),
                                          "tmp")
        self.target_file = open(os.path.join(os.path.dirname(__file__), "targets/spotify_collection_targets.json"),
                                "r+")
        self.targets = json.load(self.target_file)

    def test_get_genre(self):
        genres = self.collector.get_genre_list()
        self.assertListEqual(genres, self.targets["genres"])

    def test_get_categories(self):
        categories = self.collector.get_category_list()
        self.assertListEqual(categories, self.targets["categories"])

    def test_get_track_list(self):
        tracks = self.collector.fetch_tracks(count=1, skip=0)
        self.assertEquals(len(tracks), 32)

    def tearDown(self):
        self.target_file.close()


if __name__ == "__main__":
    unittest.main()
