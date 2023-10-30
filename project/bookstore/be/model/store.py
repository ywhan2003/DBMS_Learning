import logging
import os
import sqlite3 as sqlite
import pymongo

host = '127.0.0.1'
port = 27017
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


def init_database():
    global database_instance
    global host
    global port
    database_instance = Store(host, port)
    get_db_client()


def get_db_client():
    global database_instance
    return database_instance.get_db_client()
