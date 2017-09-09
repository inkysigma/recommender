from sqlalchemy import create_engine
from typing import List, Dict
from recommender.collector.music import Track
from recommender.collector.collector import SpotifyCollector
from sqlalchemy.orm.session import Session
import configparser


class DownloadConfiguration:
    def __init__(self, count: int, skip: int):
        self.count = count
        self.skip = skip


class DownloadManager:
    def __init__(self, sess: Session):
        self.sess = sess

    def load_tracks(self, config: DownloadConfiguration,
                    file: configparser.ConfigParser):
        collector = SpotifyCollector(file["spotify"]["id"],
                                     file["spotify"]["secret"])
        tracks = collector.get_track_list(config.count, config.skip)
        return tracks
