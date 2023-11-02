import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from be.model import store


class Seller(db_conn.DBConn):
    

    def __init__(self):
        # db_conn.DBConn.__init__(self)
        self.client = store.get_db_client()
        self.db = self.client.bookstore

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            users_col = self.db.stores

            condition = {
                "store_id": store_id,
            }

            value = {
                "book_id": book_id,
                "stock_level": stock_level,
                "book_info": book_json_str
            }

            users_col.update(condition, {"$push": {"books": value}})

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            
            users_col = self.db.stores

            condition = {
                "store_id": store_id, 
                "books.book_id": book_id 
            }
            
            users_col.update(condition, {"$inc": {"books.stock_level": add_stock_level}})

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            users_col = self.db.stores

            value = {
                "store_id": store_id,
                "user_id": user_id,
                "books": [], # book中包括书的id，库存，信息
            }
            users_col.insert_one(value)
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
