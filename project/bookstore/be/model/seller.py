import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from be.model import store
import json


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
            
            book_info = json.loads(book_json_str)
            book_name = book_info.get("title")
            author = book_info.get("author")
            publisher = book_info.get("publisher")
            book_intro = book_info.get("book_intro")
            content = book_info.get("content")
            price = book_info.get("price")


            book = {
                "book_id": book_id,
                "book_name": book_name,
                "author": author,
                "publisher": publisher,
                "book_intro": book_intro,
                "content": content,
                "stock_level": stock_level,
                "price": price
            }

            users_col.update_one({"store_id": store_id}, {"$push": {"books": book}})

            

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
            condition = {"store_id": store_id, "books.book_id": book_id}
            users_col.update_one(condition, {"$inc": {"books.$.stock_level": add_stock_level}})

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
            
            # users_col = self.db.user_store

            # users_col.insert_one({"store_id": store_id, "user_id": user_id})

            users_col = self.db.users
            users_col.update_one({"user_id": user_id}, {"$push": {"store_id": store_id}})

            users_col = self.db.stores
            users_col.insert_one({
                "store_id": store_id,
                "user_id": user_id,
                "books": []
            })
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def deliver(self, store_id, order_id) -> (int, str):
        '''
        发货
        判断这家店是否存在
        判断订单是否存在
        需要考虑订单是否付款，然后设置可能到货时间装装样子

        Inputs:
        - order_id: 订单的id
        '''

        try:

            user_col = self.db.history_orders
            result = user_col.find({"store_id":store_id})
            searching = list(result)

            if len(searching) == 0:
                return error.error_non_exist_store_id(store_id)
            

            # user_col = self.db.history_orders
            result = user_col.find({"order_id":order_id})
            searching = list(result)
            
            if len(searching) == 0:
                return error.error_not_exist_order(order_id)
            

            for each in searching:
                if each['status'] != 1:
                    return error.error_not_pay_order(order_id)
            
                else:
                    user_col.update_one({"store_id":store_id, "order_id":order_id}, {"$set":{"status":2}})


        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
