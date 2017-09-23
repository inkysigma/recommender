"""Entry point of recommender application"""
import argparse
import configparser
from recommender.train_ops import TrainingConfiguration, train
from recommender.download_ops import download

PARSER = argparse.ArgumentParser()


def configure(*files: str) -> argparse.Namespace:
    """
    Configure the application for usage.
    Returns:
        argparse.Namespace: the namespace containing the arguments parsed from the command line
    namespace"""

    PARSER.add_argument("--config-file", default="config.ini", action="store")
    PARSER.set_defaults(group="none")

    learner_parser = PARSER.add_subparsers(
        help="Select an option to either train/test/predict.")

    training_parser = learner_parser.add_parser("train")
    training_parser.set_defaults(group="learner", method="train")
    training_parser.add_argument("--disable-noise", action="store_false")
    training_parser.add_argument("--batch-size", default=10, type=int, action="store")

    test_parser = learner_parser.add_parser("test")
    test_parser.set_defaults(group="learner", method="test")

    predict_parser = learner_parser.add_parser("predict")
    predict_parser.set_defaults(group="learner", method="predict")

    download_parser = learner_parser.add_parser("download")
    download_parser.set_defaults(group="learner", method="download")
    download_parser.add_argument("--size", action="store", type=int, default=100)

    batch_parser = learner_parser.add_parser("batch")
    batch_parser.set_defaults(group="learner", method="batch")

    namespace = PARSER.parse_args()

    return namespace


def learner(flags: argparse.Namespace, configuration: configparser.ConfigParser):
    """
    Parse the flags in preparation of learning.
    Args:
        flags: the flags to parse for learning
    """
    if flags.method == "train":
        print("Starting training...")
        tflags = TrainingConfiguration(batch_size=flags.batch_size,
                                       noise=not flags.disable_noise)
        train(tflags, configuration)

    if flags.method == "download":
        print("Starting to download based on configuration...")
        download(flags, configuration)

    if flags.method == "batch":
        print("Starting to create some batches")


def main(flags):
    """
    Initializes several components based on the FLAGS declaration and
    redirects call based on the action called."""
    print(flags)
    configuration = configparser.ConfigParser(allow_no_value=True)
    configuration.read(flags.config_file)
    if flags.group == "none":
        PARSER.print_help()
    if flags.group == "learner":
        learner(flags, configuration)
    pass


if __name__ == "__main__":
    FLAGS = configure()
    main(FLAGS)
