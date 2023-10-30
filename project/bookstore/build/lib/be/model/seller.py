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
            
            store1 = {
                "store_id": store_id,
                "book_id": book_id,
                "book_info": book_json_str,
                "stock_level": stock_level
            }
            users_col.insert_one(store1)
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
            condition = {"store_id": store_id, "book_id": book_id}
            users_col.update_one(condition, {"$inc": {"stock_level": add_stock_level}})

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
            users_col = self.db.user_store

            # self.conn.execute(
            #     "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
            #     (store_id, user_id),
            # )
            users_col.insert_one({"store_id": store_id, "user_id": user_id})
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
