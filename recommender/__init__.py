"""Initialization module for recommender"""
import sys
import os

ROOT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIRECTORY)


class Configuration:
    """A generic class for configuration of modules"""
    config_file: str

    def __init__(self, config_file):
        self.config_file = config_file
