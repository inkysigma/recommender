from recommender.learner.model import LearnerModel
from recommender import Configuration


class TrainingConfiguration(Configuration):
    def __init__(self,
                 batches,
                 configuration,
                 sigmoid,
                 dropout,
                 batch_size,
                 enable_unscaled):
        self.batches = batches
        self.configuration = configuration
        self.dropout = dropout
        self.batch_size = batch_size,
        self.enable_unscaled = enable_unscaled
        self.sigmoid = sigmoid


def train(config: TrainingConfiguration):
    model = LearnerModel()
