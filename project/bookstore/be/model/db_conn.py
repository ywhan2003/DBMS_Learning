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
        db = self.client

    def store_id_exist(self, store_id):
        cursor = self.conn.execute(
            "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
