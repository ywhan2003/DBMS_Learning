from be.model import store


class DBConn:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 27017
        self.client = store.get_db_client()
        self.db = self.client.bookstore

    def user_id_exist(self, user_id):
        users_col = self.db.users
        result = list(users_col.find({"user_id": user_id}))
        if len(result) == 0:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        users_col = self.db.books
        result = list(users_col.find({"store_id": store_id, "book_id": book_id}))
        if len(result) == 0:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        users_col = self.db.stores
        result = list(users_col.find({"store_id": store_id}))
        if len(result) == 0:
            return False
        else:
            return True
