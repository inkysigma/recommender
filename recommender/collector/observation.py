from sqlalchemy import String, Column, ForeignKey
from sqlalchemy.orm import relationship
from recommender.collector import SCHEMA_BASE


class TrainingObservation(SCHEMA_BASE):
    """
    An observation for training data with a given session ID.
    """
    id = Column(String, primary_key=True)
    session = Column(String)
    track = relationship("Track")
    track_id = ForeignKey(String, "tracks.id")


class TestObservation(SCHEMA_BASE):
    """
    An observation for training data with a given session ID.
    """
    id = Column(String, primary_key=True)
    session = Column(String)
    track = relationship("Track")
    track_id = ForeignKey(String, "tracks.id")


class CrossTestObservation(SCHEMA_BASE):
    """
    An observation for training data with a given session ID.
    """
    id = Column(String, primary_key=True)
    session = Column(String)
    track = relationship("Track")
    track_id = ForeignKey(String, "tracks.id")


class SessionIds(SCHEMA_BASE):
    """
    A list of session IDs.
    """
    id = Column(String, primary_key=True)
