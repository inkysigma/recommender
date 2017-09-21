"""A module for describing how the music tracks are cached and saved."""
from recommender.collector.music import Track, Category, Genre
from sqlalchemy.orm.session import Session
from sqlalchemy import exists
from typing import List
from uuid import uuid4
import logging


class Database:
    def save_track(self, track: Track):
        pass

    def remove_track(self, tid: str):
        pass

    def update_track(self, tid: str, track: Track):
        pass

    def list_tracks(self, count: int = 100, skip: int = 0):
        pass

    def get_track(self, tid: str):
        pass

    def add_category(self, cid: str, cat: str):
        pass

    def remove_category(self, cid: str):
        pass

    def get_category(self, cat: str) -> Category:
        pass

    def add_genre(self, gid: str, gen: str):
        pass

    def remove_genre(self, gid: str):
        pass

    def get_genre(self, gen: str) -> Genre:
        pass


class RelationalDatabase(Database):
    def __init__(self, sess: Session, logger: logging.Logger):
        self.sess = sess

    def add_genre(self, gid: str, gen: str):
        """
        Add a genre to the database. If the genre already exists, nothing happens.
        Args:
            gid (str): the id of the genre as represented by the remote source. If there is no remote source,
                generating a random id is also perfectly valid.
            gen (str): the name of the genre
        """
        if self.sess.query(exists().where(Genre.genre_id == gid or Genre.genre == gen)).scalar():
            return
        genre = Genre(gid=uuid4().hex,
                      genre_id=gid,
                      genre=gen)
        self.sess.add(genre)
        self.sess.commit()

    def remove_genre(self, gid: str):
        """
        Removes a genre from the database.
        Args:
            gid (str): the id of the genre as represented by the remote source.
        """
        self.sess.query(Genre).filter(Genre.genre_id == gid).delete()
        self.sess.commit()

    def get_genre(self, gen: str) -> Genre:
        """
        Gets a genre with the specified label
        Args:
            gen (str): the genre of the music
        Returns:
            a genre representing the asked genre.
        """
        return self.sess.query(Genre).filter(Genre.genre == gen).one()

    def add_category(self, cid: str, cat: str):
        """
        Adds a category to the database.
        Args:
            cid: the category id
            cat: the name of the category
        """
        if self.sess.query(exists().where(Category.category_id == cid or Category.category == cat)).scalar():
            return
        genre = Genre(cid=uuid4().hex,
                      categorey_id=cid,
                      category=cat)
        self.sess.add(genre)
        self.sess.commit()

    def remove_category(self, cid: str):
        self.sess.query(Category).filter(Category.category_id == cid).delete()
        self.sess.commit()

    def get_category(self, cat: str) -> Category:
        return self.sess.query(Category).filter(Category.category == cat).one()

    def get_all_category(self) -> List[Category]:
        return self.sess.query(Category).all()

    def save_track(self, track: Track):
        """
        Saves a track in the database. If category_list or genre_list is used, then it will convert the strings
        into Genre and Category objects to be saved. If the track already exists, then it will be merged and updated with
        the corresponding id.
        Args:
            track: the track to add to the database
        """
        if track.track_id is not None:
            self.sess.query(Track).filter(Track.track_id == track.track_id).update(track)
        else:
            if track.category_list is not None:
                for category in track.category_list:
                    track.categories.append(self.get_category(category))
            if track.genre_list is not None:
                for genre in track.genre_list:
                    track.genres.append(self.get_genre(genre))
            self.sess.add(track)
        self.sess.commit()

    def remove_track(self, tid: str):
        self.sess.query(Track).filter(Track.track_id == tid).delete()

    def update_track(self, tid: str, track: Track):
        self.sess.query(Track).filter(Track.track_id == tid).update(track)

    def list_tracks(self, count: int = 100, skip: int = 0):
        return self.sess.query(Track).order_by(Track.track_id).skip(skip).limit(100).all()

    def get_track(self, tid: str) -> Track:
        return self.sess.query(Track).filter(Track.track_id == tid).one()
