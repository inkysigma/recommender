from recommender.collector.collector import Collector, SpotifyCollector
from recommender import Configuration
from recommender.learner.model import LearnerModel
from recommender.collector.music import Track
from recommender.collector.batch_manager import BatchManager, DatabaseBatchManager
from recommender.collector.saver import Saver, FileSaver
from recommender.collector.tools import create_batch
from recommender.collector.database import RelationalDatabase, Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import configparser
import threading
import argparse
import logging
import os
import time

IS_RUNNING = False
URL_DOWNLOADS: List[Track] = []
FILE_DELETES: List[str] = []
COMPLETED: List[Track] = []


class TrainingConfiguration(Configuration):
    def __init__(self,
                 noise,
                 batch_size,
                 mfcc):
        self.batch_size = batch_size
        self.noise = noise
        self.mfcc = mfcc


class Downloader(threading.Thread):
    def __init__(self):
        super(Downloader, self).__init__()

    def run(self):
        global IS_RUNNING
        while IS_RUNNING:
            track = URL_DOWNLOADS.pop()


class Deleter(threading.Thread):
    def __init__(self, directory: str):
        super(Deleter, self).__init__()
        self.directory = directory

    def run(self):
        global IS_RUNNING
        while IS_RUNNING:
            try:
                track = FILE_DELETES.pop()

                path = os.path.join(self.directory, track)
                os.remove(path)

                time.sleep(0.1)
            except IndexError:
                continue


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
                 file: str):
        super(Trainer, self).__init__()
        self.config = config
        self.model = model
        self.batches = batches
        self.saver = saver
        self.source = source
        self.database = database

    def run(self):
        global IS_RUNNING
        mapping = self.database.get_all_genre()
        mapping.extend(self.database.get_all_category())
        while IS_RUNNING:
            batches = self.batches.get_training_batches(10)
            self.source.fetch_track_sample([track for track, _ in batches])
            create_batch(batches, mapping, True)

    def start(self):
        super(Trainer, self).start()

    def stop(self):
        super(Trainer, self).join(10000)
        self.model.save(file=self.file)


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
        batch_manager = DatabaseBatchManager(sess, logging.getLogger("manager"),
                                             session_id=session_configuration.get("session", "id"))
    else:
        operation_logger.error("error with getting the session id. create id with batch operation")
        return

    saver = FileSaver("results/default.map", logging.getLogger("file_saver"))

    collector = SpotifyCollector(configuration.get("spotify", "id"), configuration.get("spotify", "secret"))

    config = TrainingConfiguration(
        False,
        flags.batch_size,
        32
    )
    trainer = Trainer(config,
                      model,
                      batch_manager,
                      collector,
                      saver,
                      database,
                      configuration.get("recommender", "session_file"))
    trainer.run()

    print("Press [Enter] to save the model at the snapshot.")
    while IS_RUNNING:
        input()
        IS_RUNNING = False
