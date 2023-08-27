import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_admins(self):
        """Получаем всех активных админов бота"""
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM `admins`").fetchall()

    def user_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, username,status):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute(f"INSERT INTO users VALUES({user_id},'{username}','{status}')")
        
    def update_user(self, user_id, status):
        #-----------переписать запрос !----------------------
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`,'status') VALUES(?,?)", (user_id,status))


    def delete_user(self, user_id):
        """ Удаляем пользователя"""
        with self.connection:
            return self.cursor.execute("DELETE FROM `users` WHERE `user_id` = ?", (user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()