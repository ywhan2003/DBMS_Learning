import logging
import os
import sqlite3 as sqlite
import pymongo


class Store:
    database: str
    host: str
    port: int

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_db_client(self) -> pymongo.MongoClient:
        return pymongo.MongoClient(self.host, self.port)


database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
