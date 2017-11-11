from recommender.collector.collector import Collector, SpotifyCollector
from recommender import Configuration
from recommender.learner.model import LearnerModel
from recommender.collector.music import Track
from recommender.collector.batch_manager import BatchManager, DatabaseBatchManager
from recommender.collector.saver import Saver, FileSaver
from recommender.collector.tools import create_batch
from recommender.collector.music_manager import RelationalDatabase, Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Tuple
import configparser
import threading
import argparse
import logging
import os
import time

IS_RUNNING = False
URL_DOWNLOADS: List[Track] = []
FILE_DELETES: List[str] = []
COMPLETED: List[List[Tuple[Track, str]]] = []


class TrainingConfiguration(Configuration):
    def __init__(self,
                 noise: bool,
                 batch_size: int,
                 tempdir: str,
                 mfcc: int,
                 batch_id: str):
        self.batch_size = batch_size
        self.noise = noise
        self.mfcc = mfcc
        self.tempdir = tempdir
        self.batch_id = batch_id


class DownloadConfiguration(Configuration):
    def __init__(self,
                 tempdir: str,
                 batch_size: int):
        self.tempdir = tempdir
        self.batch_size = batch_size


class Downloader(threading.Thread):
    def __init__(self,
                 collector: Collector,
                 config: DownloadConfiguration):
        super(Downloader, self).__init__()
        self.collector = collector
        self.config = config

    def run(self):
        global IS_RUNNING
        while IS_RUNNING:
            tracks = []
            i = 0
            while i < self.config.batch_size and len(URL_DOWNLOADS) > 0:
                tracks.append(URL_DOWNLOADS.pop())
            COMPLETED.append(self.collector.fetch_track_sample(self.config.tempdir, tracks))

    def stop(self):
        self.join(1000)


class DeleteRunner(threading.Thread):
    def __init__(self, directory: str):
        super(DeleteRunner, self).__init__()
        self.directory = directory

    def run(self):
        global IS_RUNNING
        while IS_RUNNING:
            try:
                track = FILE_DELETES.pop()

                path = os.path.join(self.directory, track)
                os.remove(path)

            except IndexError:
                time.sleep(2)
                continue

    def stop(self):
        self.join(1000)


class Trainer(threading.Thread):
    """
    A multi-threaded trainer with the learner model.
    """

    def __init__(self,
                 config: TrainingConfiguration,
                 model: LearnerModel,
                 batches: BatchManager,
                 source: Collector,
                 saver: Saver,
                 database: Database,
                 model_file: str):
        super(Trainer, self).__init__()
        self.config = config
        self.model = model
        self.batches = batches
        self.saver = saver
        self.source = source
        self.database = database
        self.model_file = model_file

    def run(self):
        global IS_RUNNING
        mapping = self.database.get_all_genre()
        mapping.extend(self.database.get_all_category())
        mapping.sort()

        while IS_RUNNING:
            if len(URL_DOWNLOADS) < self.config.batch_size * 3:
                track_targets_pair = self.batches.get_training_batches(self.config.batch_id, 10)
                if len(track_targets_pair) == 0:
                    IS_RUNNING = False
                    return
                URL_DOWNLOADS.extend([track for track, _ in track_targets_pair])
            if len(COMPLETED) > 0:
                tracks_file_pairs = COMPLETED.pop()
                target_file_pairs: List[Tuple[List[str], str]] = []
                for t, f in tracks_file_pairs:
                    total = [category for category in t.categories]
                    total.extend([genre for genre in t.genres])
                    target_file_pairs.append(
                        (total, f))
                batch, target = create_batch(target_file_pairs, mapping, False)
                self.model.train(batch, target)
                FILE_DELETES.extend([file for _, file in tracks_file_pairs])

    def start(self):
        super(Trainer, self).start()

    def stop(self):
        super(Trainer, self).join(10000)
        self.model.save(file=self.model_file)


def train(flags: argparse.Namespace, configuration: configparser.ConfigParser):
    global IS_RUNNING

    operation_logger = logging.getLogger("operations")

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

    database = RelationalDatabase(sess=sess, logger=logging.getLogger("database"))
    database.get_all_category()

    model = LearnerModel(
        categories=database.genre_size() + database.category_size(),
        logger=logging.getLogger("learner_model")
    )

    session_file = configuration.get("recommender", "session_file")

    session_configuration = configparser.ConfigParser()
    session_configuration.read_file(session_file)

    if session_configuration.get("session", "id"):
        batch_manager = DatabaseBatchManager(sess, logging.getLogger("manager"))
    else:
        operation_logger.error("error with getting the session id. create id with batch operation")
        return

    saver = FileSaver("results/default.map", logging.getLogger("file_saver"))

    collector = SpotifyCollector(configuration.get("spotify", "id"), configuration.get("spotify", "secret"))

    if configuration.get("recommender", "cache_directory") and not os.path.exists(
            configuration.get("recommender", "cache_directory")):
        os.makedirs(configuration.get("recommender", "cache_directory"))

    tempdir = configuration.get("recommender", "cache_directory") if configuration.get("recommender",
                                                                                       "cache_directory") else ""

    training_config = TrainingConfiguration(
        False,
        flags.batch_size,
        tempdir,
        32,
        session_configuration.get("session", "id")
    )
    download_config = DownloadConfiguration(
        tempdir,
        flags.batch_size
    )
    trainer = Trainer(training_config,
                      model,
                      batch_manager,
                      collector,
                      saver,
                      database,
                      configuration.get("recommender", "session_file"))

    downloader = Downloader(collector,
                            download_config)

    deleter = DeleteRunner(tempdir)

    downloader.run()
    deleter.run()
    trainer.run()

    print("Press [Enter] to save the model at the snapshot.")
    while IS_RUNNING:
        input()
        IS_RUNNING = False
