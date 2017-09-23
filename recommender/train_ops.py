from recommender.collector.collector import Collector
from recommender import Configuration
from recommender.learner.model import LearnerModel
from recommender.collector.batch_manager import BatchManager
from recommender.collector.saver import Saver
from recommender.collector.tools import create_batch
from recommender.collector.database import RelationalDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import configparser
import threading
import argparse
import logging
import os

IS_RUNNING = False


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
                 file: str):
        super(Trainer, self).__init__()
        self.config = config
        self.model = model
        self.batches = batches
        self.saver = saver
        self.source = source
        self.file = file

    def run(self):
        global IS_RUNNING
        while IS_RUNNING:
            batches = self.batches.get_training_batches(10)
            self.source.fetch_track_sample([track for track, _ in batches])
            create_batch(batches)

    def start(self):
        super(Trainer, self).start()

    def stop(self):
        super(Trainer, self).join(10000)
        self.model.save(file=self.file)


def train(flags: argparse.Namespace, configuration: configparser.ConfigParser):
    global IS_RUNNING

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
    database = RelationalDatabase(sess=sess, logger=logging.getLogger("database"))
    database.get_all_category()

    learner_log_file = configuration.get("logging", "learner_model")
    if learner_log_file:
        if not os.path.exists(learner_log_file):
            if not os.path.exists(os.path.dirname(learner_log_file)):
                os.makedirs(os.path.dirname(learner_log_file))
        logging.getLogger("database").addHandler(logging.FileHandler(learner_log_file, mode="a+"))

    model = LearnerModel(
        categories=database.genre_size() + database.category_size(),
        logger=logging.getLogger("learner_model")
    )

    batch_manager = BatchManager()
    config = TrainingConfiguration(
        False,
        flags.batch_size,
        32
    )
    trainer = Trainer(config,
                      model)

    print("Press [Enter] to save the model at the snapshot.")
    while IS_RUNNING:
        input()
        IS_RUNNING = False
