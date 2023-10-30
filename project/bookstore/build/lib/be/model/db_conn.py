from be.model import store


class DBConn:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 27017
        self.client = store.get_db_client()
        self.db = self.client.bookstore
        self.db.users.create_index([("user_id", 1)], unique=True)
        self.db.stores.create_index([("store_id", 1), ("book_id", 1)], unique=True)
        self.db.user_store.create_index([("store_id", 1), ("user_id", 1)], unique=True)
        self.db.new_order.create_index([("order_id", 1)], unique=True)
        self.db.new_order_detail.create_index([("order_id", 1), ("book_id", 1)], unique=True)

    def user_id_exist(self, user_id):
        users_col = self.db.users
        result = list(users_col.find({"user_id": user_id}))
        if len(result) == 0:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        users_col = self.db.stores
        result = list(users_col.find({"store_id": store_id, "book_id": book_id}))
        if len(result) == 0:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        # users_col = self.db.stores
        users_col = self.db.user_store
        result = list(users_col.find({"store_id": store_id}))
        if len(result) == 0:
            return False
        else:
            return True
