from sqlalchemy import String, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from recommender.collector import SCHEMA_BASE


class TrainingObservation(SCHEMA_BASE):
    """
    An observation for training data with a given session ID.
    """
    __tablename__ = "training_observations"
    id = Column(String, primary_key=True)
    session = Column(String)
    track = relationship("Track")
    track_id = Column(String, ForeignKey("tracks.track_id"))


class TestObservation(SCHEMA_BASE):
    """
    An observation for test data with a given session ID.
    """
    __tablename__ = "test_observations"
    id = Column(String, primary_key=True)
    session = Column(String)
    track = relationship("Track")
    track_id = Column(String, ForeignKey("tracks.track_id"))


class CrossTestObservation(SCHEMA_BASE):
    """
    An observation for cross test data with a given session ID.
    """
    __tablename__ = "cross_test_observation"
    id = Column(String, primary_key=True)
    session = Column(String)
    track = relationship("Track")
    track_id = Column(String, ForeignKey("tracks.track_id"))


class BatchSessions(SCHEMA_BASE):
    """
    A list of session IDs.
    """
    __tablename__ = "batch_sessions"
    batch_id = Column(String, primary_key=True)
    # the number of songs from each category
    count = Column(Integer)
