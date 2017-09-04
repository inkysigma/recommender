"""A module for describing how the music tracks are cached and saved."""
from recommender.collector.music import Track, Category, Genre
from sqlalchemy.orm.session import Session


class Database:
    def save_track(self, track: Track):
        pass

    def remove_track(self, track: Track):
        pass

    def update_track(self, id: str, track: Track):
        pass

    def list_tracks(self, count: int = 100, skip: int = 0):
        pass

    def get_track(self, id: str):
        pass

    def add_category(self, cat: Category):
        pass

    def remove_category(self, id: str):
        pass

    def add_genre(self, gen: Genre):
        pass

    def remove_genre(self, id: str):
        pass

class RmdbDatabase(Database):
    def __init__(self, sess: Session):
        self.sess = sess

    def save_track(self, track: Track):
        self.sess.query(Track)
