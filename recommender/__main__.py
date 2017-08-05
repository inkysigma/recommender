"""Entry point of recommender application"""
import argparse


def configure(*files: str) -> (argparse.Namespace, dict):
    parser = argparse.ArgumentParser()
    learner_parser = parser.add_subparsers(
        help="Select an option to either train/test/predict.")

    training_parser = learner_parser.add_parser("train")
    training_parser.set_defaults(method="train")

    test_parser = learner_parser.add_parser("test")
    test_parser.set_defaults(method="test")

    predict_parser = learner_parser.add_parser("predict")
    predict_parser.set_defaults(method="predict")

    flags = parser.parse_args()

    return flags, None


def main(flags):
    """Initializes several components based on the FLAGS declaration."""
    pass


if __name__ == "__main__":
    flags, file_config = configure()
    print(flags)
    main(flags)
