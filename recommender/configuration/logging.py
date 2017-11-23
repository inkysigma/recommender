from . import LOG_FORMATTER
from recommender import ROOT_DIRECTORY
import logging
import argparse
import configparser
import os
import sys


def __create_log__(file: str, name: str):
    """
    Configure a logger to have the necessary handlers and file outputs
    Args:
        file (str): the name of the file to log to
        name (str): the name of the logger
    """
    if file:
        file = os.path.join(ROOT_DIRECTORY, file)
        if not os.path.exists(file):
            if not os.path.exists(os.path.dirname(file)) and os.path.dirname(file) != '':
                os.makedirs(os.path.dirname(file))
        logger = logging.getLogger(name)
        handler = logging.FileHandler(file, mode="a+")
        handler.setFormatter(LOG_FORMATTER)
        logger.addHandler(handler)
    logging.getLogger(name).addHandler(logging.StreamHandler(sys.stdout))


def configure(args: argparse.Namespace, config: configparser.ConfigParser):
    __create_log__(config.get("logging", "manager"), "manager")
    __create_log__(config.get("logging", "learner_model"), "learner_model")
    __create_log__(config.get("logging", "database"), "database")
    __create_log__(config.get("logging", "saver"), "saver")
    __create_log__(config.get("logging", "operation"), "operation")
