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
                 download_all: bool = False) -> None:
        self.count = count
        self.skip = skip
        self.all = download_all
        self.spotify_id = spotify_id
        self.spotify_secret = spotify_secret
        self.use_cached = use_cached


class DownloadOperator:
    """
    A manager for downloading tracks.
    """

    def __init__(self, sess: Session, logger: logging.Logger) -> None:
        self.sess = sess
        self.database = RelationalDatabase(self.sess, logging.getLogger("download_database"))
        self.logger = logger

    def load_tracks(self, config: DownloadConfiguration) -> None:
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


def download(flags: argparse.Namespace, configuration: configparser.ConfigParser) -> None:
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

    manager = DownloadOperator(sess, logging.getLogger("manager"))

    download_config = DownloadConfiguration(
        int(configuration.get("download", "count")),
        int(configuration.get("download", "skip")),
        configuration.get("spotify", "id"),
        configuration.get("spotify", "secret"),
        configuration.getboolean("download", "use_cached"),
        download_all=configuration.getboolean("download", "all", fallback=False)
    )
    manager.load_tracks(download_config)
