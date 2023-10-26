from be.model import store


class DBConn:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 27017
        self.client = store.get_db_client()

    def user_id_exist(self, user_id):
        db = self.client.bookstore
        users_col = db.users
        result = list(users_col.find({"user_id": user_id}))
        if len(result) == 0:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        db = self.client.bookstore
        users_col = db.books
        result = list(users_col.find({"store_id": store_id, "book_id": book_id}))
        if len(result) == 0:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        db = self.client.bookstore
        users_col = db.stores
        result = list(users_col.find({"store_id": store_id}))
        if len(result) == 0:
            return False
        else:
            return True
