from recommender.collector.batch_manager import DatabaseBatchManager, BatchManager
import argparse
import logging
import configparser


class BatchConfiguration:
    def __init__(self,
                 training_count: int = 0,
                 test_count: int = 0,
                 cross_test_count: int = 0,
                 session_id: str = ""):
        self.training_count = training_count
        self.test_count = test_count
        self.cross_test_count = cross_test_count
        self.session_id = session_id


class BatchOperator:
    def __init__(self, manager: BatchManager, logger: logging.Logger):
        self.manager = manager
        self.logging = logger

    def create_batch(self, config: BatchConfiguration):
        self.manager.create_batches()

    def add_batch(self, config: BatchConfiguration):
        pass

    def list_batches(self, config: BatchConfiguration):
        pass

    def use_batch(self, config: BatchConfiguration):
        pass


def create_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    pass


def add_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    pass


def list_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    pass


def use_batch(args: argparse.Namespace, config: configparser.ConfigParser):
    pass
