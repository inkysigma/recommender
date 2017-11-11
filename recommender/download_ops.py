from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from recommender.collector.music_manager import RelationalDatabase
from recommender.collector.collector import SpotifyCollector
from sqlalchemy.orm.session import Session
import configparser
import logging
import os
import argparse


class DownloadConfiguration:
    def __init__(self,
                 count: int,
                 skip: int,
                 spotify_id: str,
                 spotify_secret: str,
                 use_cached: bool = True,
                 all: bool = False):
        self.count = count
        self.skip = skip
        self.all = all
        self.spotify_id = spotify_id
        self.spotify_secret = spotify_secret
        self.use_cached = use_cached


class DownloadOperator:
    """
    A manager for downloading tracks.
    """

    def __init__(self, sess: Session, logger: logging.Logger):
        self.sess = sess
        self.database = RelationalDatabase(self.sess, logging.getLogger("download_database"))
        self.logger = logger

    def load_tracks(self, config: DownloadConfiguration):
        """
        Load tracks into the database and their targets
        Args:
            config: the configuration as given from the command line
                and file system
        """
        collector = SpotifyCollector(config.spotify_id,
                                     config.spotify_secret)
        self.logger.info("Starting to download tracks.")

        if not config.use_cached:
            categories = collector.get_category_list()
            genres = collector.get_genre_list()
            for category in categories:
                self.logger.info(f"Added category: {collector.get_category_name(category)}")
                self.database.add_category(category, collector.get_category_name(category))
            for genre in genres:
                self.logger.info(f"Added genre: {genre}")
                self.database.add_genre(genre, genre)
        cats = self.database.get_all_category()
        maps = collector.fetch_tracks(cats, self.database.exists_track, config.count, config.skip, config.all)
        for cat, tracks in maps:
            for track in tracks:
                self.database.save_track(track)


def download(flags: argparse.Namespace, configuration: configparser.ConfigParser):
    driver = configuration.get("rmdb", "engine")
    host = configuration.get("rmdb", "host")
    port = configuration.get("rmdb", "port")
    username = configuration.get("rmdb", "username")
    password = configuration.get("rmdb", "password")
    database = configuration.get("rmdb", "database")

    session = sessionmaker()
    engine = create_engine(f"{driver}://{username}:{password}@{host}:{port}/{database}")
    session.configure(bind=engine)
    sess = session()

    database_logging_file = configuration.get("logging", "database")
    if database_logging_file:
        if not os.path.exists(database_logging_file):
            if not os.path.exists(os.path.dirname(database_logging_file)):
                os.makedirs(os.path.dirname(database_logging_file))
        logging.getLogger("database").addHandler(logging.FileHandler(database_logging_file, mode="a+"))

    manager = DownloadOperator(sess, logging.getLogger("download_manager"))

    download_config = DownloadConfiguration(
        int(configuration.get("download", "count")),
        int(configuration.get("download", "skip")),
        configuration.get("spotify", "id"),
        configuration.get("spotify", "secret"),
        configuration.getboolean("download", "use_cached"),
        all=configuration.getboolean("download", "all", fallback=False)
    )
    manager.load_tracks(download_config)
