"""Entry point of recommender application"""
import argparse
from recommender.learner.model import LearnerModel


def configure(*files: str) -> argparse.Namespace:
    """
    Configure the application for usage.
    Returns:
        argparse.Namspace: the namespace containing the arguments parsed from the command line
    namespace"""
    parser = argparse.ArgumentParser()

    parser.add_argument("--config-file", default="config.ini", action="store")
    parser.add_argument("--enable-sigmoid", action="store_true")
    parser.add_argument("--disable-dropout", action="store_false")

    learner_parser = parser.add_subparsers(
        help="Select an option to either train/test/predict.")

    training_parser = learner_parser.add_parser("train")
    training_parser.set_defaults(group="learner", method="train")
    training_parser.add_argument("--use-gpu", action="store_true")
    training_parser.add_argument("--disable-noise", action="store_false")
    training_parser.add_argument("--batch-size", default=10, type=int, action="store")
    training_parser.add_argument("--batch-file", type=str, action="store")
    training_parser.add_argument("--enable-unscaled", action="store_true")

    test_parser = learner_parser.add_parser("test")
    test_parser.set_defaults(group="learner", method="test")

    predict_parser = learner_parser.add_parser("predict")
    predict_parser.set_defaults(group="learner", method="predict")

    manage_parser = learner_parser.add_parser("manage")
    manage_parser.set_defaults(group="learner", method="manage")

    namespace = parser.parse_args()

    return namespace

def learner(flags: argparse.Namespace):
    """
    Parse the flags in preparation of learning.
    Args:
        flags: the flags to parse for learning
    """
    if flags.method == "train":
        print("Starting training...")
        print("Press [Enter] to save the model at the snapshot.")



def main(flags):
    """
    Initializes several components based on the FLAGS declaration and
    redirects call based on the action called."""
    if flags.group == "learner":
        learner(flags)
    pass


if __name__ == "__main__":
    FLAGS = configure()
    main(FLAGS)
