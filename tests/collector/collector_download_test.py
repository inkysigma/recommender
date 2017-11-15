from recommender.collector.music import Track
from recommender.collector.collector import SpotifyCollector
import unittest
import configparser
import json
import os
from . import ROOT_DIR


class SpotifyCollectorDownloadTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("test.ini") and not os.path.exists("../test.ini") and not os.path.exists(os.path.join(ROOT_DIR, "test.ini")):
            print("File test.ini not found")
            print(f"Current directory is: {os.path.dirname(os.path.abspath(__file__))}")

        config = configparser.ConfigParser()
        config.read("test.ini")

        if not os.path.exists("test.ini") and not os.path.exists("../test.ini"):
            config.read(os.path.join(ROOT_DIR, "test.ini"))
        else:
            config.read("../test.ini")

        self.collector = SpotifyCollector(config.get("spotify", "client_id"),
                                          config.get("spotify", "client_secret"),
                                          "tmp")
        self.target_file = open(os.path.join(os.path.dirname(__file__), "targets/spotify_collection_targets.json"),
                                "r+")
        self.targets = json.load(self.target_file)

    def test_download(self):
        track = Track(
            url=b"https://p.scdn.co/mp3-preview/1f789c77d7e08e3328de28114f4ef7a2e840b631?cid=8897482848704f2a8f8d7c79726a70d4",
            track_id="test")
        samples = self.collector.fetch_track_sample([track])
        print(samples[0])

    def tearDown(self):
        self.target_file.close()


if __name__ == "__main__":
    unittest.main()
