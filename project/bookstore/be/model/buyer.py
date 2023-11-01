import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model import store


class Buyer(db_conn.DBConn):
    

    def __init__(self):
        # db_conn.DBConn.__init__(self)
        self.client = store.get_db_client()
        self.db = self.client.bookstore

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                # cursor = self.conn.execute(
                #     "SELECT book_id, stock_level, book_info FROM store "
                #     "WHERE store_id = ? AND book_id = ?;",
                #     (store_id, book_id),
                # )
                users_col = self.db.stores
                result = users_col.find({"store_id": store_id, "book_id": book_id})
                searching = list(result)
                if len(searching) == 0:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = None
                book_info = None
                for each in searching:
                    stock_level = each["stock_level"]
                    book_info = each["book_info"]
                    
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count),
                # )

                condition = {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}}
                result = users_col.update_one(condition, {"$inc": {"stock_level": -count}})

                cnt = result.modified_count
                if cnt == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # self.conn.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #     "VALUES(?, ?, ?, ?);",
                #     (uid, book_id, count, price),
                # )

                users_col = self.db.new_order_detail
                value = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                users_col.insert_one(value)

            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id),
            # )
            users_col = self.db.new_order
            value = {
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id
            }
            users_col.insert_one(value)
            
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # cursor = conn.execute(
            #     "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
            #     (order_id,),
            # )

            buyer_id = None
            store_id = None

            users_col = self.db.new_order
            result = users_col.find({"order_id": order_id})
            searching = list(result)
            cnt = len(searching)

            if cnt == 0:
                return error.error_invalid_order_id(order_id)

            for each in searching:
                buyer_id = each["user_id"]
                store_id = each["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # cursor = conn.execute(
            #     "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            # )
            users_col = self.db.users
            result = users_col.find({"user_id": buyer_id})
            searching = list(result)
            cnt = len(searching)
 
            if cnt == 0:
                return error.error_non_exist_user_id(buyer_id)
            
            balance = None
            password1 = None

            for each in searching:
                balance = each["balance"]
                password1 = each["password"]

            if password != password1:
                return error.error_authorization_fail()

            # cursor = conn.execute(
            #     "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
            #     (store_id,),
            # )

            users_col = self.db.user_store
            result = users_col.find({"store_id": store_id})
            searching = list(result)
            cnt = len(searching)

            if cnt == 0:
                return error.error_non_exist_store_id(store_id)

            seller_id = None

            for each in searching:
                seller_id = each["user_id"]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # cursor = conn.execute(
            #     "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
            #     (order_id,),
            # )

            users_col = self.db.new_order_detail
            result = users_col.find({"order_id": order_id})
            searching = list(result)
            
            total_price = 0
            for row in searching:
                count = row["count"]
                price = row["price"]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # cursor = conn.execute(
            #     "UPDATE user set balance = balance - ?"
            #     "WHERE user_id = ? AND balance >= ?",
            #     (total_price, buyer_id, total_price),
            # )

            users_col = self.db.users
            condition = {
                "user_id": buyer_id, 
                "balance": {"$gte": total_price}
            }
            result = users_col.update_one(condition, {"$inc": {"balance": -total_price}})
            cnt = result.modified_count

            if cnt == 0:
                return error.error_not_sufficient_funds(order_id)
            
            

            # cursor = conn.execute(
            #     "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
            #     (total_price, buyer_id),
            # )

           
            condition = {
                "user_id": buyer_id, 
            }
            result = users_col.update_one(condition, {"$inc": {"balance": total_price}})
            cnt = result.modified_count

            if cnt == 0:
                return error.error_non_exist_user_id(buyer_id)
            
            

            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )

            users_col = self.db.new_order
            condition = {
                "order_id": order_id
            }
            result = users_col.find(condition)
            searching = list(result)
            cnt = len(searching)
            if cnt == 0:
                return error.error_invalid_order_id(order_id)
            
            users_col.delete_one(condition)

            # cursor = conn.execute(
            #     "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            # )

            users_col = self.db.new_order_detail
            result = users_col.find(condition)
            searching = list(result)
            cnt = len(searching)

            if cnt == 0:
                return error.error_invalid_order_id(order_id)
            
            users_col.delete_one(condition)

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # cursor = self.conn.execute(
            #     "SELECT password  from user where user_id=?", (user_id,)
            # )

            users_col = self.db.users
            result = users_col.find({"user_id": user_id})
            searching = list(result)
            
            if len(searching) == 0:
                return error.error_authorization_fail()

            for each in searching:
                if each["password"] != password:
                    return error.error_authorization_fail()

            # cursor = self.conn.execute(
            #     "UPDATE user SET balance = balance + ? WHERE user_id = ?",
            #     (add_value, user_id),
            # )
            result = users_col.update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})

            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)
            

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    

    def search_books(self, search_method: str, 
                     keywords: str, 
                     whether_all: bool = True, 
                     page_num: int = 1,
                     page_limit: int = 20) -> (int, str):
        '''
        搜索图书

        Inputs:
        - search_method: 搜索方式，题目，标签，目录，内容等
        - keywords: 搜索关键词
        - whether_all: 是否为全站搜索
        - page_num: 页数
        - page_limit: 每一页限制的显示条数
        '''

    
    def cancel_order(self, user_id: str, password: str, order_id: str) -> (int, str):
        '''
        取消订单

        Inputs:
        - user_id: 用户id
        - password: 用户密码
        - order_id: 需要取消的订单的id
        '''


    def search_order(self, user_id: str, password: str) -> (int, str):
        '''
        查询订单

        Inputs:
        - user_id: 用户id
        - password: 用户密码
        '''


    def receive(self, user_id: str, password: str, order_id: str) -> (int, str):
        '''
        收货

        需要考虑是否发货，是否到货，不发货或者不到货都不能收货
        到货可能会有点难，需要考虑时间戳，到货也可以另外再写一个函数
        就是在new_order_detail的每一条里面加入每一个动作的时间

        Inputs:
        - user_id: 用户id
        - password: 用户密码
        - order_id: 需要取消的订单的id
        '''


    def deliver(self, order_id) -> (int, str):
        '''
        发货

        需要考虑订单是否付款，然后设置可能到货时间装装样子

        Inputs:
        - order_id: 订单的id
        '''

    
    def reach(self, order_id) -> (int, str):
        '''
        到货
        '''