"""Entry point of recommender application"""
import argparse
import configparser
import os
from recommender.train_ops import train
from recommender.download_ops import download
from recommender.configuration.logging import configure as configure_logging

PARSER = argparse.ArgumentParser()


def configure() -> argparse.Namespace:
    """
    Configure the application for usage.
    Returns:
        argparse.Namespace: the namespace containing the arguments parsed from the command line
    namespace
    """

    PARSER.add_argument("--config-file", default="config.ini", action="store")
    PARSER.set_defaults(group="none")

    learner_parser = PARSER.add_subparsers(
        help="Select an option to either train/test/predict."
    )

    training_parser = learner_parser.add_parser("train")
    training_parser.set_defaults(group="learner", method="train")
    training_parser.add_argument("--disable-noise", action="store_false")
    training_parser.add_argument("--batch-size", default=10, type=int, action="store")

    test_parser = learner_parser.add_parser("test")
    test_parser.set_defaults(group="learner", method="test")

    predict_parser = learner_parser.add_parser("predict")
    predict_parser.set_defaults(group="learner", method="predict")

    batch_parser = learner_parser.add_parser("batch")
    batch_parser.set_defaults(group="learner", method="batch")

    download_parser = learner_parser.add_parser("download")
    download_parser.set_defaults(group="database", method="download")
    download_parser.add_argument("--size", action="store", type=int, default=100)

    namespace = PARSER.parse_args()

    return namespace


def learner(flags: argparse.Namespace, configuration: configparser.ConfigParser):
    """
    Parse the flags in preparation of learning.
    Args:
        flags: the flags to parse for learning
        configuration: the configuration given by the config file
    """
    if flags.method == "train":
        print("Starting training...")
        train(flags, configuration)

    if flags.method == "batch":
        print("Starting to create some batches...")


def database(flags: argparse.Namespace, configuration: configparser.ConfigParser):
    if flags.method == "download":
        print("Starting to download based on configuration...")
        download(flags, configuration)


def main(flags: argparse.Namespace):
    """
    Initializes several components based on the FLAGS declaration and
    redirects call based on the action called."""
    namespace = vars(flags)
    configuration = configparser.ConfigParser(allow_no_value=True)
    if not os.path.exists(namespace["config_file"]):
        print("Please create a configuration file")
        return
    configuration.read_file(open(namespace["config_file"], "r"))

    configure_logging(flags, configuration)
    if flags.group == "none":
        PARSER.print_help()
    if flags.group == "learner":
        learner(flags, configuration)
    if flags.group == "database":
        database(flags, configuration)


if __name__ == "__main__":
    FLAGS = configure()
    main(FLAGS)
