from recommender.collector.batch_manager import DatabaseBatchManager, BatchManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import argparse
import logging
import configparser
import os


class BatchConfiguration:
    def __init__(self,
                 session: Session,
                 training_count: int = 0,
                 test_count: int = 0,
                 cross_test_count: int = 0,
                 session_file: str = ""):
        self.training_count = training_count
        self.test_count = test_count
        self.cross_test_count = cross_test_count
        self.session = session
        self.session_file = session_file


class BatchOperator:
    def __init__(self, config: BatchConfiguration, logger: logging.Logger):
        self.config = config
        self.logging = logger
        self.file_config = configparser.ConfigParser()
        if os.path.exists(config.session_file):
            self.file_config.read(config.session_file)

    def write_config(self):
        with open(self.config.session_file, "w+") as file:
            self.file_config.write(file)

    def create_batch(self):
        manager = DatabaseBatchManager(self.config.session, logging.getLogger("manager"))
        bid = manager.create_batches(self.config.training_count, self.config.test_count, self.config.cross_test_count)
        self.file_config.set("session", "id", bid)
        self.file_config.set("session", "training_count", self.config.training_count)
        self.file_config.set("session", "test_count", self.config.test_count)
        self.file_config.set("session", "cross_test_count", self.config.cross_test_count)
        self.file_config.set("session", "training_index", 0)
        self.file_config.set("session", "test_index", 0)
        self.file_config.set("session", "cross_test_index", 0)
        self.write_config()

    def extend_batch(self):
        manager = DatabaseBatchManager(self.config.session, logging.getLogger("manager"))

        manager.extend_batches(self.file_config.get("session", "id"),
                               self.config.training_count,
                               self.config.test_count,
                               self.config.cross_test_count)
        self.file_config.set("session", "training_count",
                             self.file_config.getint("session", "training_count") + self.config.training_count)
        self.file_config.set("session", "test_count",
                             self.file_config.getint("session", "test_count") + self.config.test_count)
        self.file_config.set("session", "cross_test_count",
                             self.file_config.getint("session", "cross_test_count") + self.config.cross_test_count)
        self.write_config()

    def list_batches(self):
        manager = DatabaseBatchManager(self.config.session, logging.getLogger("manager"))
        print("Batches available:")
        for batch in manager.list_sessions():
            print(f"{batch}")

    def use_batch(self):
        manager = DatabaseBatchManager(self.config.session, logging.getLogger("manager"))
        incomplete = True
        batch_id = ""
        training_count = 0
        test_count = 0
        cross_test_count = 0
        while incomplete:
            batch_id = input("Enter the id of the batch:")
            if batch_id is None:
                return
            try:
                training_count, test_count, cross_test_count = manager.get_session(batch_id)
            except ValueError:
                print("Enter a valid id.")

        self.file_config.set("session", "id", batch_id)
        self.file_config.set("session", "training_count", training_count)
        self.file_config.set("session", "test_count", test_count)
        self.file_config.set("session", "cross_test_count", cross_test_count)
        self.file_config.set("session", "training_index", 0)
        self.file_config.set("session", "test_index", 0)
        self.file_config.set("session", "cross_test_index", 0)
        self.write_config()


def create_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    operation_logger = logging.getLogger("operations")

    driver = config.get("rmdb", "engine")
    host = config.get("rmdb", "host")
    port = config.get("rmdb", "port")
    username = config.get("rmdb", "username")
    password = config.get("rmdb", "password")
    database = config.get("rmdb", "database")

    session = sessionmaker()
    engine = create_engine(f"{driver}://{username}:{password}@{host}:{port}/{database}")
    session.configure(bind=engine)
    sess = session()

    config = BatchConfiguration(sess,
                                config.getint("init", "training_count"),
                                config.getint("init", "test_count"),
                                config.getint("init", "cross_test_count"))

    operator = BatchOperator(config, operation_logger)
    operator.create_batch()


def extend_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    operation_logger = logging.getLogger("operations")

    driver = config.get("rmdb", "engine")
    host = config.get("rmdb", "host")
    port = config.get("rmdb", "port")
    username = config.get("rmdb", "username")
    password = config.get("rmdb", "password")
    database = config.get("rmdb", "database")

    session = sessionmaker()
    engine = create_engine(f"{driver}://{username}:{password}@{host}:{port}/{database}")
    session.configure(bind=engine)
    sess = session()

    config = BatchConfiguration(sess,
                                config.getint("init", "training_count"),
                                config.getint("init", "test_count"),
                                config.getint("init", "cross_test_count"))

    operator = BatchOperator(config, operation_logger)
    operator.extend_batch()


def list_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    pass


def use_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    pass
