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

# users数据库：原来的+自己开的店的编号+曾经的order_id数组
# stores数据库：将book数组嵌套在里面，这样可以和user_store合并起来
# orders：orderid，书，书的数量，下单时间，订单状态，把new_order和new_order_detail合并起来
