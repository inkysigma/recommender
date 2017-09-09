from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


class BASE:
    """A base sqlachelmy class that helps serialization of the object"""

    def __json__(self, request):
        json_exclude = getattr(self, '__json_exclude__', set())
        return {key: value for key, value in self.__dict__.items()
                if not key.startswith('_')
                and key not in json_exclude}


SCHEMA_BASE = declarative_base(cls=BASE)


def initialize_database(engine) -> None:
    """Initialize the sql components with the given engine"""
    SCHEMA_BASE.metadata.bind = engine
    SCHEMA_BASE.metadata.create_all(engine)


__all__ = ["music", "learner"]
