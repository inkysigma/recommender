"""A module for describing how the music tracks are cached and saved."""
from recommender.collector.music import Track, Category, Genre
from sqlalchemy.orm.session import Session
from sqlalchemy import exists, func, and_
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

    def exists_track(self, tid: str):
        pass

    def add_category(self, cid: str, cat: str):
        pass

    def remove_category(self, cid: str):
        pass

    def get_category(self, cat: str) -> Category:
        pass

    def fetch_category(self, cid: str) -> Category:
        pass

    def add_genre(self, gid: str, gen: str):
        pass

    def fetch_genre(self, gid: str) -> Genre:
        pass

    def remove_genre(self, gid: str):
        pass

    def get_genre(self, gen: str) -> Genre:
        pass

    def get_all_genre(self) -> List[Genre]:
        pass

    def get_all_category(self) -> List[Category]:
        pass


class RelationalDatabase(Database):
    def __init__(self, sess: Session, logger: logging.Logger):
        self.sess = sess
        self.logging = logger

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
        self.logging.info(f"adding genre: {gen} with id {gid}")
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
        self.logging.info(f"removing genre: {gid}")
        self.sess.query(Genre).filter(Genre.genre_id == gid).delete()
        self.sess.commit()

    def fetch_genre(self, gid: str):
        """
        Gets a genre object based on the internal id used
        Args:
            gid (str): the internal id

        Returns:
            Genre: a genre object
        """
        self.logging.info(f"fetching genre: {gid}")
        return self.sess.query(Genre).filter(Genre.gid == gid).one()

    def get_genre(self, gen: str) -> Genre:
        """
        Gets a genre with the specified label
        Args:
            gen (str): the genre of the music
        Returns:
            a genre representing the asked genre.
        """
        self.logging.log(15, f"getting genre: {gen}")
        return self.sess.query(Genre).filter(Genre.genre == gen).one()

    def add_category(self, cid: str, cat: str):
        """
        Adds a category to the database.
        Args:
            cid: the category id
            cat: the name of the category
        """
        self.logging.info(f"adding category: {cat} with it {cid}")
        if self.sess.query(exists().where(Category.category_id == cid or Category.category == cat)).scalar():
            return
        genre = Genre(cid=uuid4().hex,
                      categorey_id=cid,
                      category=cat)
        self.sess.add(genre)
        self.sess.commit()

    def remove_category(self, cid: str):
        self.logging.info(f"removing category: {cid}")
        self.sess.query(Category).filter(Category.category_id == cid).delete()
        self.sess.commit()

    def fetch_category(self, cid: str):
        self.logging.info(f"getting category: {cid}")
        return self.sess.query(Category).filter(Category.cid == cid).one()

    def get_category(self, cat: str) -> Category:
        self.logging.log(15, f"getting category: {cat}")
        return self.sess.query(Category).filter(Category.category == cat).one()

    def get_all_category(self) -> List[Category]:
        self.logging.info(f"getting all categories")
        return self.sess.query(Category).all()

    def save_track(self, track: Track):
        """
        Saves a track in the database. If category_list or genre_list is used, then it will convert the strings
        into Genre and Category objects to be saved. If the track already exists, then it will be merged and updated with
        the corresponding id.
        Args:
            track: the track to add to the database
        """
        if track.internal_id is not None:
            self.logging.info(f"updated track: {track.track_id} for {track.title}")
            self.sess.query(Track).filter(Track.track_id == track.track_id).update(track)
        elif self.sess.query(self.sess.query(exists().where(and_(Track.title == track.title,
                                                           Track.artist == track.artist,
                                                           Track.url == track.url)).exists()).scalar()) \
                .scalar():

            self.logging.info(f"updated track w/o id: {track.title} by {track.artist}")
            self.sess.query(Track).filter(and_(Track.title == track.title,
                                               Track.artist == track.artist,
                                               Track.url == track.url)).update(track)
        else:
            self.logging.info(f"added track: {track.title} by {track.artist}")
            if track.category_list is not None:
                for category in track.category_list:
                    cat = self.fetch_category(category)
                    track.categories.append(cat)
                    cat.tracks.append(track)
            if track.genre_list is not None:
                for genre in track.genre_list:
                    gen = self.fetch_genre(genre)
                    track.genres.append(gen)
                    gen.tracks.append(track)
            track.internal_id = uuid4().hex
            self.sess.add(track)
        self.sess.commit()

    def remove_track(self, tid: str):
        self.logging.info(f"removing track: {tid}")
        self.sess.query(Track).filter(Track.track_id == tid).delete()

    def update_track(self, tid: str, track: Track):
        self.logging.info(f"update track: {tid}")
        self.sess.query(Track).filter(Track.track_id == tid).update(track)

    def list_tracks(self, count: int = 100, skip: int = 0):
        self.logging.info("listing tracks")
        return self.sess.query(Track).order_by(Track.track_id).skip(skip).limit(100).all()

    def get_track(self, tid: str) -> Track:
        self.logging.info(f"getting track: {tid}")
        return self.sess.query(Track).filter(Track.track_id == tid).one()

    def get_all_genre(self) -> List[Genre]:
        self.logging.info("getting all genres")
        return self.sess.query(Genre).all()

    def genre_size(self) -> int:
        self.logging.info("getting size of all genres")
        return self.sess.query(func.count(Genre.genre_id)).scalar()

    def category_size(self) -> int:
        self.logging.info("getting size of all genres")
        return self.sess.query(func.count(Category.genre_id)).scalar()
