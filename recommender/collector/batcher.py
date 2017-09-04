from sqlalchemy.orm.session import Session
import numpy as np
import recommender.collector.music as music


class Batch:
    def __init__(self, data: music.Track, target: np.ndarray):
        self.data = data
        self.target = target


class Batcher:
    def get_batches(self, count: int = 10) -> Batch:
        pass


class DatabaseBatcher(Batcher):
    def __init__(self, sess: Session):
        self.__skip__ = 0
        self.__sess__ = sess

    def get_batches(self, count: int = 10) -> Batch:
        pass
