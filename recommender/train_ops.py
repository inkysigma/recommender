from recommender.collector.collector import Collector
from recommender import Configuration
from recommender.learner.model import LearnerModel
from recommender.collector.batcher import Batcher
import configparser
import threading


class TrainingFlags(Configuration):
    def __init__(self,
                 noise,
                 batch_size):
        self.batch_size = batch_size
        self.noise = noise


class Trainer(threading.Thread):
    """
    A multi-threaded trainer with the learner model.
    """

    def __init__(self, model: LearnerModel, batches: Batcher, source: Collector, file: str):
        super(Trainer, self).__init__()
        self.model = model
        self.batches = batches
        self.file = file
        self.is_running = False
        self.source = source

    def run(self):
        while (self.is_running):
            batch = self.batches.get_batches()
            track = self.source.get_track(batch.data)
            self.model.train(track, batch.target)

    def start(self):
        self.is_running = True
        super(Trainer, self).start()

    def stop(self):
        self.is_running = False
        super(Trainer, self).join(10000)
        self.model.save(file=self.file)


def train(flags: TrainingFlags, configuration: configparser.ConfigParser) -> Trainer:
    pass
