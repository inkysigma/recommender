"""Declares the models of music such as Tracks and Collections"""
from sqlalchemy import String, Column, Table, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from recommender.collector import SCHEMA_BASE
from typing import List

TRACK_CATEGORY_ASSOCIATION = Table("track_category_association", SCHEMA_BASE.metadata,
                                   Column("track_id", String, ForeignKey("tracks.track_id")),
                                   Column("category_id", String, ForeignKey("categories.cid"))
                                   )

TRACK_GENRE_ASSOCIATION = Table("track_genre_association", SCHEMA_BASE.metadata,
                                Column("track_id", String, ForeignKey("tracks.track_id")),
                                Column("genre_id", String, ForeignKey("genres.gid")))


class Track(SCHEMA_BASE):
    """A track representing a song that can be collected"""
    __tablename__ = "tracks"
    internal_id = Column(String, primary_key=True)
    internal_count = Column(Integer, index=True)

    track_id = Column(String)
    url = Column(String)
    title = Column(String)
    artist = Column(String)

    categories = relationship("Category",
                              secondary=TRACK_CATEGORY_ASSOCIATION,
                              back_populates="tracks")
    genres = relationship("Genre",
                          secondary=TRACK_GENRE_ASSOCIATION,
                          back_populates="tracks")

    last_trained = Column(DateTime)

    genre_list: List[str] = []
    category_list: List[str] = []

    training_session = relationship("TrainingObservation", back_populates="track")
    test_session = relationship("TestObservation", back_populates="track")
    cross_test_session = relationship("CrossTestObservation", back_populates="track")

    def __str__(self):
        return f"{self.track_id}: {self.title} by {artist}"

    def __repr__(self):
        return self.__str__()


class Category(SCHEMA_BASE):
    """A category of tracks"""
    __tablename__ = "categories"

    """
    The internal id of the category
    """
    cid = Column(String, primary_key=True)

    """
    The remote id of the category to be used
    """
    category_id = Column(String)
    category = Column(String)
    location = Column(String)
    tracks = relationship("Track",
                          secondary=TRACK_CATEGORY_ASSOCIATION,
                          back_populates="categories")


class Genre(SCHEMA_BASE):
    """Genre for a music"""
    __tablename__ = "genres"
    gid = Column(String, primary_key=True)

    genre_id = Column(String)
    genre = Column(String)
    tracks = relationship("Track",
                          secondary=TRACK_GENRE_ASSOCIATION,
                          back_populates="genres")
