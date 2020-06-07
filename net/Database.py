import sqlite3


class Database:
    def __init__(self, database_name: str = None):
        self.__database_name = database_name

    def __get_connection(self):
        client = sqlite3.connect(self.database_name)

    @property
    def database_name(self):
        return self.__database_name
