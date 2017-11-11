from sqlalchemy.orm.session import Session
import recommender.collector.observation as obs
from . import music
from typing import List, Tuple
import uuid
import logging


class BatchManager:
    def get_training_batches(self, batch_id: str, count: int = 10, skip: int = 0) -> List[Tuple[music.Track, List[str]]]:
        pass

    def get_test_batches(self, batch_id: str, count: int = 10, skip: int = 0) -> List[Tuple[music.Track, List[str]]]:
        pass

    def get_cross_test_batches(self, batch_id: str, count: int = 10, skip: int = 0) -> List[Tuple[music.Track, List[str]]]:
        pass

    def create_batches(self, training_count: int, test_count: int, cross_test_count: int, skip: int = 0):
        pass

    def extend_batches(self, batch_id: str, training_count: int, test_count: int, cross_test_count: int, skip: int = 0):
        pass

    def list_sessions(self) -> List[str]:
        pass

    def get_session(self, batch_id: str) -> (int, int, int):
        pass


class DatabaseBatchManager(BatchManager):
    def __init__(self, sess: Session, logger: logging.Logger):
        self.__sess__ = sess
        self.__logging__ = logger
        self.__generated__ = False

    def get_training_batches(self, batch_id: str, count: int = 10, skip: int = 0) -> List[Tuple[music.Track, List[str]]]:
        """
        Uses the specified database connection to get a list of training batches of the specified size.
        In addition, the number of songs to skip over should be kept track of externally. The result is a
        list of Track, List[str] pairs where Track is the track object as stored in the database. List[str] is
        the list of targets for the given track. If the session id is not specified, then this will return empty.
        Args:
            batch_id: the id of the batch
            count: the number of batch-pairs to fetch from the database. If there are not enough remaining
                then only the remaining will be returned
            skip: the number of tracks to skip. Use this value to present the number of tracks to skip over
                after training them

        Returns:
            List[(music.Track, List[str])]: the list of batch-pairs retrieved from the database.
        """
        if batch_id is None:
            return []

        queries = []
        tracks = self.__sess__.query(obs.TrainingObservation) \
            .filter(obs.TrainingObservation.session == batch_id) \
            .order_by(obs.TrainingObservation.id) \
            .skip(skip) \
            .limit(count) \
            .all()

        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def get_test_batches(self, batch_id: str, count: int = 10, skip: int = 0) -> List[Tuple[music.Track, List[str]]]:
        """
        Uses the specified database connection to get a list of test batches of the specified size.
        In addition, the number of songs to skip over should be kept track of externally. The result is a
        list of Track, List[str] pairs where Track is the track object as stored in the database. List[str] is
        the list of targets for the given track. If the session id is not specified, then this will return empty.
        Args:
            batch_id: the id of the batch
            count: the number of batch-pairs to fetch from the database. If there are not enough remaining
                then only the remaining will be returned
            skip: the number of tracks to skip. Use this value to present the number of tracks to skip over
                after training them

        Returns:
            List[(music.Track, List[str])]: the list of batch-pairs retrieved from the database.
        """
        if batch_id is None:
            return []
        queries = []
        tracks = self.__sess__.query(obs.TestObservation) \
            .filter(obs.TestObservation.session == batch_id) \
            .order_by(obs.TestObservation.id) \
            .skip(skip) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def get_cross_test_batches(self, batch_id: str, count: int = 10, skip: int = 0) -> List[Tuple[music.Track, List[str]]]:
        """
        Uses the specified database connection to get a list of cross-test batches of the specified size.
        In addition, the number of songs to skip over should be kept track of externally. The result is a
        list of Track, List[str] pairs where Track is the track object as stored in the database. List[str] is
        the list of targets for the given track. If the session id is not specified, then this will return empty.
        Args:
            batch_id (str): the id of the batch
            count (int): the number of batch-pairs to fetch from the database. If there are not enough remaining
                then only the remaining will be returned
            skip (int): the number of tracks to skip. Use this value to present the number of tracks to skip over
                after training them

        Returns:
            List[(music.Track, List[str])]: the list of batch-pairs retrieved from the database.
        """
        if batch_id is None:
            return []
        queries = []
        tracks = self.__sess__.query(obs.CrossTestObservation) \
            .filter(obs.CrossTestObservation.session == batch_id) \
            .order_by(obs.CrossTestObservation.id) \
            .skip(skip) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def create_batches(self, training_count: int, test_count: int, cross_test_count: int, skip: int = 0) -> str:
        """
        Create a set of batches of the given sizes. Can be used to initialize a batch and the __id__ will be
        automatically set to the new session id. If the request is unable to be fulfilled, an empty string is returned \
        and the transaction is not committed.
        Args:
            training_count (int): the number of training examples to use
            test_count (int): the number of test examples to use
            cross_test_count (int): the number of cross test examples to use
            skip (int): the number of tracks to skip

        Returns:
            str: the new session id for the batch
        """
        tracks = self.__sess__.query(music.Track) \
            .order_by(music.Track.track_id) \
            .skip(skip) \
            .limit(training_count + test_count + cross_test_count) \
            .all()

        if len(tracks) < training_count + test_count + cross_test_count:
            raise BufferError()
        batch_id = uuid.uuid4().hex

        self.__sess__.add(obs.BatchSessions(id=batch_id,
                                            count=training_count + test_count + cross_test_count))

        self.__sess__.bulk_save_objects([
            obs.TrainingObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=batch_id)
            for i in range(0, min(len(tracks), training_count))
        ])

        self.__sess__.bulk_save_objects([
            obs.TestObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=batch_id)
            for i in range(training_count, min(len(tracks), training_count + test_count))
        ])

        self.__sess__.bulk_save_objects([
            obs.CrossTestObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i],
                                     session=batch_id)
            for i in
            range(training_count + test_count, min(len(tracks), training_count + test_count + cross_test_count))
        ])

        self.__sess__.commit()
        return batch_id

    def extend_batches(self, batch_id: str, training_count: int, test_count: int, cross_test_count: int,
                       skip: int = 0) -> None:
        """
        Extend the batches to include more training, tests, and cross tests
        Args:
            batch_id (str): the id of the batch
            training_count (int): the number of training examples to add
            test_count (int): the number of test examples to add
            cross_test_count (int): the number of cross tests examples to add
            skip (int): the number of tracks to skip
        """
        if batch_id is None:
            raise ValueError("batch_id was not supplied")
        batch: obs.BatchSessions = self.__sess__.query(obs.BatchSessions).filter(
            obs.BatchSessions == batch_id).one_or_none()

        if batch is None:
            raise ValueError("batch_id was not created")

        tracks = self.__sess__.query(music.Track) \
            .order_by(music.Track.track_id) \
            .skip(batch.count + skip) \
            .limit(training_count + test_count + cross_test_count) \
            .all()
        if len(tracks) < training_count + test_count + cross_test_count:
            raise BufferError()

        self.__sess__.add(obs.BatchSessions(id=batch_id,
                                            skip=0,
                                            count=training_count + test_count + cross_test_count))

        self.__sess__.bulk_save_objects([
            obs.TrainingObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=batch_id)
            for i in range(0, min(len(tracks), training_count))
        ])

        self.__sess__.bulk_save_objects([
            obs.TestObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=batch_id)
            for i in range(training_count, min(len(tracks), training_count + test_count))
        ])

        self.__sess__.bulk_save_objects([
            obs.CrossTestObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i],
                                     session=batch_id)
            for i in
            range(training_count + test_count, min(len(tracks), training_count + test_count + cross_test_count))
        ])

        batch.count += training_count + test_count + cross_test_count
        self.__sess__.commit()

    def list_sessions(self) -> List[str]:
        """
        List the sessions available.
        Returns:
            a list of the available sessions
        """
        return [sess.id for sess in self.__sess__.query(obs.BatchSessions).all()]

    def get_session(self, batch_id: str) -> (int, int, int):
        """
        Get the properties of a session
        Args:
            batch_id (str): the id of the batch

        Returns:
            (int, int, int) -> a tuple of training_count, test_count, and cross_test_count
        """

        if batch_id is None:
            raise ValueError("batch_id was not supplied")
        batch: obs.BatchSessions = self.__sess__.query(obs.BatchSessions).filter(
            obs.BatchSessions == batch_id).one_or_none()

        if batch is None:
            raise ValueError("batch_id was not created")

        return (
            self.__sess__.query(obs.TrainingObservation).filter(obs.TrainingObservation.session == batch_id).count(),
            self.__sess__.query(obs.TrainingObservation).filter(obs.TestObservation.session == batch_id).count(),
            self.__sess__.query(obs.CrossTestObservation).filter(obs.CrossTestObservation.session == batch_id).count()
        )
