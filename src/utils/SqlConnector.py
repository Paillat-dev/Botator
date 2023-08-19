from sqlite3 import connect
from random import randint


class SQLConnection:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()


class _sql:
    @property
    def mainDb(self):
        s = connect("./database/data.db")
        return SQLConnection(s)


sql: _sql = _sql()
