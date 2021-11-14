import sqlite3


class SQLighter:

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def add_user(self, users):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `email`) VALUES (?, ?)", users)

    def user_exist(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,))
            return bool(len(result.fetchall()))

    def check_email(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `email` FROM `users` WHERE `user_id` = ?", (user_id,))
            return result.fetchall()

    def select_all(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users`")
            return result.fetchall()

    def close_base(self):
        self.connection.close()
