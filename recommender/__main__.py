"""Entry point of recommender application"""
import argparse
from recommender.learner.model import LearnerModel


def configure(*files: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    learner_parser = parser.add_subparsers(
        help="Select an option to either train/test/predict.")

    training_parser = learner_parser.add_parser("train")
    training_parser.set_defaults(method="train")
    training_parser.add_argument("--use-gpu", action="store_true")

    test_parser = learner_parser.add_parser("test")
    test_parser.set_defaults(method="test")

    predict_parser = learner_parser.add_parser("predict")
    predict_parser.set_defaults(method="predict")

    namespace = parser.parse_args()

    return namespace


def main(flags):
    """Initializes several components based on the FLAGS declaration."""
    pass


if __name__ == "__main__":
    FLAGS = configure()
    main(FLAGS)
