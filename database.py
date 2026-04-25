import sqlite3

class DatabaseManager:
    def __init__(self, db_file = "robot.db"):
        self.db_file = db_file
        self.create_table()
    
    def get_connect(self):
        return sqlite3.connect(self.db_file)
    
    def create_table(self):
        with self.get_connect() as connect:
            connect.execute('''CREATE TABLE IF NOT EXISTS
                            history(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT NOT NULL,
                            group_id TEXT,
                            role TEXT NOT NULL,
                            text TEXT NOT NULL,
                            timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
                            )''')
            connect.execute('''CREATE TABLE IF NOT EXISTS
                            tarot_history(
                            id  INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT NOT NULL,
                            card_name TEXT NOT NULL,
                            timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
                            )''')
            connect.execute('''CREATE TABLE IF NOT EXISTS
                            tarot_content(
                            id  INTEGER PRIMARY KEY AUTOINCREMENT,
                            card_name TEXT NOT NULL,
                            card_text TEXT NOT NULL,
                            card_path TEXT NOT NULL
                            )''')
    
    def fetch_data(self, sql, params=()):
        with self.get_connect() as connect:
            cursor = connect.execute(sql, params)
            return cursor.fetchall()
    
    def execute_action(self, sql, params=()):
        with self.get_connect() as connect:
            connect.execute(sql, params)
    
    def takeout(self, table, column, table_format = None, params = ()):
        if (table_format):
            sql = f"SELECT {column} FROM {table} WHERE {table_format}"
        else:
            sql = f"SELECT {column} FROM {table}"
        return self.fetch_data(sql, params)

    def deposit(self, table, column, table_format, params):
        sql = f"INSERT INTO {table} {column} VALUES {table_format}"
        self.execute_action(sql, params)



