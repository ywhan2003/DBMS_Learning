import jwt
import time
import logging
import sqlite3 as sqlite
from be.model import error
from be.model import db_conn

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second
    

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.users_col = self.db.users

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
    
            user1 = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            } 
            self.users_col.insert_one(user1)
        except Exception as e:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        # cursor = self.conn.execute("SELECT token from user where user_id=?", (user_id,))
        
        token1 = None
        result = self.users_col.find({"user_id": user_id})
        for each in result:
            token1 = each["token"]
        
        if token1 is None:
            return error.error_authorization_fail()
        db_token = token1
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        # cursor = self.conn.execute(
        #     "SELECT password from user where user_id=?", (user_id,)
        # )
        password1 = None
        result = self.users_col.find({"user_id": user_id})
        for each in result:
            password1 = each["password"]
        
        if password1 is None:
            return error.error_authorization_fail()

        if password != password1:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            condition = {"user_id": user_id}
            self.users_col.update_one(condition, {"$set": {"token": token, "terminal": terminal}})
            result = list(self.users_col.find(condition))
            if len(result) == 0:
                return error.error_authorization_fail() + ("",)
        
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            
            condition = {"user_id": user_id}
            self.users_col.update_one(condition, {"$set": {"token": dummy_token, "terminal": terminal}})
            result = list(self.users_col.find(condition))
            if len(result) == 0:
                return error.error_authorization_fail()
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            result = list(self.users_col.find({"user_id": user_id}))
            flag = 1
            self.users_col.delete_one({"user_id": user_id})
            if flag == 1:
                pass
            else:
                return error.error_authorization_fail()
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            # cursor = self.conn.execute(
            #     "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?",
            #     (new_password, token, terminal, user_id),
            # )

            condition = {"user_id": user_id}
            self.users_col.update_one(condition, {"$set": {"token": token, "terminal": terminal, "password": new_password}})
            result = list(self.users_col.find(condition))
            if len(result) == 0:
                return error.error_authorization_fail()
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
