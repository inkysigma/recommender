"""Declares the models of music such as Tracks and Collections"""
from sqlalchemy import String, Column
from recommender.collector import SCHEMA_BASE

class Track(SCHEMA_BASE):
    """A track representing a song that can be collected"""
    tid = Column(String, primary_key=True)
    url = Column(String)
    title = Column(String)
    genre = Column(String)
    artist = Column(String)

class Categorey(SCHEMA_BASE):
    """A category of tracks."""
    cid = Column(String, primary_key=True)
    categorey_id = Column(String)
    name = Column(String)
    location = Column(String)