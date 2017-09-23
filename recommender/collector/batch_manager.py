from sqlalchemy.orm.session import Session
import recommender.collector.music as music
import recommender.collector.observation as obs
from typing import List
import uuid


class BatchManager:
    def get_training_batches(self, count: int = 10, skip: int = 0) -> List[(music.Track, List[str])]:
        pass

    def get_test_batches(self, count: int = 10, skip: int = 0) -> List[(music.Track, List[str])]:
        pass

    def get_cross_test_batches(self, count: int = 10, skip: int = 0) -> List[(music.Track, List[str])]:
        pass

    def create_batches(self, starting_index: int, training_count: int, test_count: int, cross_test_count: int):
        pass


class DatabaseBatchManager(BatchManager):
    def __init__(self, sess: Session, session_id: str = None):
        self.__sess__ = sess
        self.__id__ = session_id

    def get_training_batches(self, count: int = 10, skip: int = 0) -> List[(music.Track, List[str])]:
        """
        Uses the specified database connection to get a list of training batches of the specified size.
        In addition, the number of songs to skip over should be kept track of externally. The result is a
        list of Track, List[str] pairs where Track is the track object as stored in the database. List[str] is
        the list of targets for the given track. If the session id is not specified, then this will return empty.
        Args:
            count: the number of batch-pairs to fetch from the database. If there are not enough remaining
                then only the remaining will be returned
            skip: the number of tracks to skip. Use this value to present the number of tracks to skip over
                after training them

        Returns:
            List[(music.Track, List[str])]: the list of batch-pairs retrieved from the database.
        """
        if self.__id__ is None:
            return []
        queries = []
        tracks = self.__sess__.query(obs.TrainingObservation) \
            .filter(obs.TrainingObservation.session == self.__id__) \
            .order_by(obs.TrainingObservation.id) \
            .skip(skip) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def get_test_batches(self, count: int = 10, skip: int = 0) -> List[(music.Track, List[str])]:
        """
        Uses the specified database connection to get a list of test batches of the specified size.
        In addition, the number of songs to skip over should be kept track of externally. The result is a
        list of Track, List[str] pairs where Track is the track object as stored in the database. List[str] is
        the list of targets for the given track. If the session id is not specified, then this will return empty.
        Args:
            count: the number of batch-pairs to fetch from the database. If there are not enough remaining
                then only the remaining will be returned
            skip: the number of tracks to skip. Use this value to present the number of tracks to skip over
                after training them

        Returns:
            List[(music.Track, List[str])]: the list of batch-pairs retrieved from the database.
        """
        if self.__id__ is None:
            return []
        queries = []
        tracks = self.__sess__.query(obs.TestObservation) \
            .filter(obs.TestObservation.session == self.__id__) \
            .order_by(obs.TestObservation.id) \
            .skip(skip) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def get_cross_test_batches(self, count: int = 10, skip: int = 0) -> List[(music.Track, List[str])]:
        """
        Uses the specified database connection to get a list of cross-test batches of the specified size.
        In addition, the number of songs to skip over should be kept track of externally. The result is a
        list of Track, List[str] pairs where Track is the track object as stored in the database. List[str] is
        the list of targets for the given track. If the session id is not specified, then this will return empty.
        Args:
            count: the number of batch-pairs to fetch from the database. If there are not enough remaining
                then only the remaining will be returned
            skip: the number of tracks to skip. Use this value to present the number of tracks to skip over
                after training them

        Returns:
            List[(music.Track, List[str])]: the list of batch-pairs retrieved from the database.
        """
        if self.__id__ is None:
            return []
        queries = []
        tracks = self.__sess__.query(obs.CrossTestObservation) \
            .filter(obs.CrossTestObservation.session == self.__id__) \
            .order_by(obs.CrossTestObservation.id) \
            .skip(skip) \
            .limit(count) \
            .all()
        for t in tracks:
            queries.append((t.track, [item.category for item in t.track.categories].extend(
                [item.genre for item in t.track.genres])))
        return queries

    def create_batches(self, starting_index: int, training_count: int, test_count: int, cross_test_count: int) -> str:
        """
        Create a set of batches of the given sizes. Can be used to initialize a batch and the __id__ will be
        automatically set to the new session id. If the request is unable to be fulfilled, an empty string is returned \
        and the transaction is not committed.
        Args:
            starting_index (int): the starting index of the database to select for
            training_count (int): the number of training examples to use
            test_count (int): the number of test examples to use
            cross_test_count (int): the number of cross test examples to use

        Returns:
            str: the new session id for the batch
        """
        tracks = self.__sess__.query(music.Track) \
            .order_by(music.Track.track_id) \
            .skip(music.Track.track_id) \
            .limit(training_count + test_count + cross_test_count) \
            .all()

        if len(tracks) < training_count + test_count + cross_test_count:
            return ""

        if not self.__id__:
            self.__id__ = uuid.uuid4().hex
            generated = True
        else:
            generated = False

        self.__sess__.bulk_save_objects([
            obs.TrainingObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=self.__id__)
            for i in range(0, min(len(tracks), training_count))
        ])
        self.__sess__.bulk_save_objects([
            obs.TestObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=self.__id__)
            for i in range(training_count, min(len(tracks), training_count + test_count))
        ])
        self.__sess__.bulk_save_objects([
            obs.CrossTestObservation(id=uuid.uuid4().hex, track_id=tracks[i].track_id, track=tracks[i], session=self.__id__)
            for i in
            range(training_count + test_count, min(len(tracks), training_count + test_count + cross_test_count))
        ])
        if generated:
            self.__sess__.add(obs.BatchSessions(id=self.__id__))
        self.__sess__.commit()
        return self.__id__
