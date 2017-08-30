"""Entry point of recommender application"""
import argparse


def configure(*files: str) -> argparse.Namespace:
    """
    Configure the application for usage.
    Returns:
        argparse.Namspace: the namespace containing the arguments parsed from the command line
    namespace"""
    parser = argparse.ArgumentParser()
    learner_parser = parser.add_subparsers(
        help="Select an option to either train/test/predict.")

    training_parser = learner_parser.add_parser("train")
    training_parser.set_defaults(method="train")

    # TODO: Add methods to build the model like turning on GPU support.
    # Creating GPU groups and using them
    # Selecting files to load and save to

    test_parser = learner_parser.add_parser("test")
    test_parser.set_defaults(method="test")

    predict_parser = learner_parser.add_parser("predict")
    predict_parser.set_defaults(method="predict")

    manage_parser = learner_parser.add_parser("manage")
    manage_parser.set_defaults(method="manage")

    flags = parser.parse_args()

    return flags, None


def main(flags):
    """Initializes several components based on the FLAGS declaration."""
    pass


if __name__ == "__main__":
    flags, file_config = configure()
    print(flags)
    main(flags)
