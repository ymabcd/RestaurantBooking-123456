from abc import ABC, abstractmethod


class DBAPI(ABC):
    @abstractmethod
    def name(self):
        pass


class DatabaseAPI(DBAPI):
    def __init__(self, name="MySon_DB"):
        self._name = name

    @property
    def name(self):
        return self._name


class LogSystem:
    def __init__(self, db):
        self._db = db

    def log_message(self, content):
        return f'[{self._db.name}] {content}'