import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model import store
import time

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
                return error.error_non_exist_user_id(user_id) + (uid,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (uid,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            books = []
            for book_id, count in id_and_count:
                # cursor = self.conn.execute(
                #     "SELECT book_id, stock_level, book_info FROM store "
                #     "WHERE store_id = ? AND book_id = ?;",
                #     (store_id, book_id),
                # )
                users_col = self.db.stores
                result = users_col.find({"store_id": store_id, "books": {"$elemMatch": {"book_id": book_id}}},
                                        {"books": {"$elemMatch": {"book_id": book_id}}}
                                        )
                
                searching = list(result)
                if len(searching) == 0:
                    return error.error_non_exist_book_id(book_id) + (uid,)

                stock_level = None
                # book_info = None
                price = 0
                for each in searching:
                    for book in each["books"]:
                        stock_level = book["stock_level"]
                        price = book["price"]
                    
                # book_info_json = json.loads(book_info)
                # price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (uid,)

                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count),
                # )

                condition = {"store_id": store_id, "books.book_id": book_id, "books.stock_level": {"$gte": count}}
                result = users_col.update_one(condition, {"$inc": {"books.$.stock_level": -count}})

                cnt = result.modified_count
                if cnt == 0:
                    return error.error_stock_level_low(book_id) + (uid,)

                # self.conn.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #     "VALUES(?, ?, ?, ?);",
                #     (uid, book_id, count, price),
                # )

                
                book = {
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                books.append(book)

            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id),
            # )
            
            users_col = self.db.history_orders
            value = {
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id,
                "books": books,
                "status": 0,
                "time": time.time()
            }

            users_col.insert_one(value)

            users_col = self.db.users
            users_col.update_one({"user_id": user_id}, {"$push": {"orders": uid}})
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", uid

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # cursor = conn.execute(
            #     "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
            #     (order_id,),
            # )

            buyer_id = None
            store_id = None

            users_col = self.db.history_orders
            result = users_col.find({"order_id": order_id, "status": 0})
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

            # users_col = self.db.user_store
            # result = users_col.find({"store_id": store_id})
            # searching = list(result)
            # cnt = len(searching)

            # if cnt == 0:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            seller_id = None
            users_col = self.db.stores
            result = users_col.find({"store_id": store_id})
            searching = list(result)
            for each in searching:
                seller_id = each["user_id"]
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # cursor = conn.execute(
            #     "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
            #     (order_id,),
            # )

            total_price = 0
            
            users_col = self.db.history_orders
            result = users_col.find({"store_id": store_id, "order_id": order_id, "status": 0})
            searching = list(result)
            
            for each in searching:
                books = each["books"]
                for row in books:
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
            
            users_col = self.db.history_orders
            users_col.update_one({"order_id": order_id, "store_id": store_id, "status": 0}, {"$set": {"status": 1}})

            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )

            

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
                     store_id: str = None, 
                     page_num: int = 1,
                     page_limit: int = 20) -> (int, str):
        '''
        搜索图书

        Inputs:
        - search_method: 搜索方式，题目，标签, 内容等
        - keywords: 搜索关键词
        - store_id: 是否为全站搜索
        - page_num: 页数
        - page_limit: 每一页限制的显示条数
        '''
        right_method = ["title", "tags", "content", "book_intro", "author"]

        try:
            
            # 判断搜索的方式是否合法
            if not search_method in right_method:
                return error.error_searching_method(search_method)
            
            # 选择文档集
            users_col = self.db.stores
            result = None

            # 如果store_id是None，则全站搜索
            if store_id is None:

                result = users_col.find(
                    {"books": {"$elemMatch": {search_method: {'$regex': keywords}}}}
                ).skip(page_limit*(page_num -1)).limit(page_limit)

            # 反之，则在指定的店铺内搜索
            else:
                result = users_col.find(
                    {"store_id": store_id, "books":{"$elemMatch": {search_method: {'$regex': keywords}}}}
                ).skip(page_limit*(page_num - 1)).limit(page_limit)

            # 判断是否搜到结果
            # searching = list(result)
            # a = searching[0]['store_id']
            # if len(searching) == 0:
            #     return error.error_contains_keywords(keywords)

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        
        except BaseException as e:
            return 530, "{}".format(str(e))
        
        return 200, 'ok'
        

    
    def cancel_order(self, user_id: str, password: str, order_id: str) -> (int, str):
        '''
        取消订单

        Inputs:
        - user_id: 用户id
        - password: 用户密码
        - order_id: 需要取消的订单的id
        '''
        try:
            user_col = self.db.users
            stores_col = self.db.stores
            order_col = self.db.history_orders

            # user是否存在， 密码是否正确
            result = user_col.find({"user_id":user_id})
            user_searching = list(result)
            
            if len(user_searching) == 0:
                return error.error_not_exist_user_id(user_id)

            for each in user_searching:
                if each["password"] != password:
                    return error.error_authorization_fail()
                
            
            result = order_col.find({"order_id":order_id})
            order_searching = list(result)

            if len(order_searching) == 0:
                return error.error_not_exist_order(order_id)
            
            for each in order_searching:
                # store_id = each['store_id']
                if each['status'] >= 2:
                    return error.error_can_not_cancel(order_id)


    
                elif each['status'] == 1:   
                    store_id = each['store_id']

                    for book in each['books']:

                        stores_col.update_one(
                            {"store_id":store_id, "books.book_id":book['book_id']}, 
                            {"$inc":{"books.$.stock_level": book['count']}}
                        )

                        user_col.update_one(
                            {"user_id":user_id},
                            {"$inc":{"balance": book['price']*book['count']}}
                        )
                        # user_col.delete_one(
                        #     {"user_id":user_id},
                        #     {"$pull":{"order_id":order_id}}
                        # )
                        
                order_col.delete_one({"order_id":order_id})
                        
                        
        
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, 'ok'


    def search_order(self, user_id: str, password: str) -> (int, str):
        '''
        查询订单

        Inputs:
        - user_id: 用户id
        - password: 用户密码
        '''

        try:
            user_col = self.db.users
            result = user_col.find({"user_id":user_id})
            searching = list(result)
            
            if len(searching) == 0:
                return error.error_exist_user_id(user_id)

            for each in searching:
                if each["password"] != password:
                    return error.error_authorization_fail()
                

            user_col = self.db.history_orders
                
            orders = user_col.find({"user_id":user_id})
            
            if len(list(orders)) == 0:
                return error.error_not_exist_order(user_id)


        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e)) 
        return 200, 'ok'


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
        try:
            user_col = self.db.users
            result = user_col.find({"user_id":user_id})
            searching = list(result)
            
            if len(searching) == 0:
                return error.error_exist_user_id(user_id)

            for each in searching:
                if each["password"] != password:
                    return error.error_authorization_fail()
                
            user_col = self.db.history_orders
            result = user_col.find({"order_id":order_id})
            searching  = list(result)

            if len(searching) == 0:
                return error.error_not_exist_order(order_id)


            for each in searching:
                if each['status'] != 2:
                    return error.error_not_reach_order(order_id)
                else:
                    user_col.update_one({"order_id":order_id}, {"$set":{"status":3}})

        
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, 'ok'