from sqlalchemy import create_engine
from typing import List, Dict
from recommender.collector.database import RelationalDatabase
from recommender.collector.collector import SpotifyCollector
from sqlalchemy.orm.session import Session
import configparser
import logging


class DownloadConfiguration:
    def __init__(self, count: int,
                 skip: int,
                 tempdir: str,
                 print_progress: bool = True):
        self.count = count
        self.skip = skip
        self.tempdir = tempdir
        self.print_progress = print_progress


class DownloadManager:
    """
    A manager for downloading tracks.
    """

    def __init__(self, sess: Session):
        self.sess = sess
        self.database = RelationalDatabase(self.sess, logging.getLogger("download_database"))

    def load_tracks(self, config: DownloadConfiguration,
                    file: configparser.ConfigParser,
                    logger: logging.Logger):
        """
        Load tracks into the database and their targets
        Args:
            config: the configuration as given from the command line
            file: the configuration file as a ConfigParser
            logger: the logger to use while downloading
        """
        collector = SpotifyCollector(file.get("spotify", "id"),
                                     file.get("spotify", "secret"),
                                     config.tempdir)
        logger.log(2, "Starting to download tracks.")
        if not file.getboolean("recommender", "use_cached"):
            categories = collector.get_category_list()
            genres = collector.get_genre_list()
            for category in categories:
                self.database.add_category(category, collector.get_category_name(category))
            for genre in genres:
                self.database.add_genre(genre, collector.get_genre_name(genre))
        maps = collector.get_track_list(config.count, config.skip)
        for cat, tracks in maps:
            for track in tracks:
                self.database.save_track(track)
