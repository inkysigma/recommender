from sqlalchemy.orm.session import Session
import recommender.collector.music as music
import recommender.collector.observation as obs
from typing import List


class Batcher:
    def get_training_batches(self, count: int = 10) -> List[(music.Track, List[str])]:
        pass

    def get_test_batches(self, count: int = 10) -> List[(music.Track, List[str])]:
        pass

    def get_cross_test_batches(self, count: int = 10) -> List[(music.Track, List[str])]:
        pass

    def create_batches(self, training_count: int, test_count: int, cross_test_count: int):
        pass


class DatabaseBatcher(Batcher):
    def __init__(self, sess: Session, session_id: str):
        self.__skip__ = 0
        self.__sess__ = sess
        self.__id__ = session_id

    def get_training_batches(self, count: int = 10) -> List[(music.Track, List[str])]:
        queries = []
        tracks = self.__sess__.query(obs.TrainingObservation) \
            .filter(obs.TrainingObservation.session == self.__id__) \
            .order_by(obs.TrainingObservation.id) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def get_test_batches(self, count: int = 10) -> List[(music.Track, List[str])]:
        queries = []
        tracks = self.__sess__.query(obs.TestObservation) \
            .filter(obs.TestObservation.session == self.__id__) \
            .order_by(obs.TestObservation.id) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def get_cross_test_batches(self, count: int = 10) -> List[(music.Track, List[str])]:
        queries = []
        tracks = self.__sess__.query(obs.CrossTestObservation) \
            .filter(obs.CrossTestObservation.session == self.__id__) \
            .order_by(obs.CrossTestObservation.id) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def create_batches(self, training_count: int, test_count: int, cross_test_count: int):
        pass
