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
                            id           INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id      TEXT NOT NULL,
                            group_id     TEXT,
                            role         TEXT NOT NULL,
                            content      TEXT NOT NULL,
                            tool_calls   TEXT,
                            tool_call_id TEXT,
                            timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
                            )''')
            connect.execute('''CREATE TABLE IF NOT EXISTS
                            tarot_history(
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id   TEXT NOT NULL,
                            card_name TEXT NOT NULL,
                            timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
                            )''')
            connect.execute('''CREATE TABLE IF NOT EXISTS
                            tarot_content(
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
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

    def deposit_chat_history(self, role, user_id, group_id, content, tool_calls, too_call_id):
        self.deposit("history", "(role, user_id, group_id, content, tool_calls, tool_call_id)", "(?, ?, ?, ?, ?, ?)", (role, user_id, group_id, content, tool_calls, too_call_id))

    def deposit_tarot_history(self, user_id, card_name):
        self.deposit("tarot_history", "(user_id, card_name)", "(?, ?)", (user_id, card_name))

    def takeout_chat_history(self, user_id, group_id):
        if group_id:
            history_text = self.takeout("history", "role, content, tool_calls, tool_call_id", "user_id = ? AND group_id = ?", (user_id, group_id))
        else:
            history_text = self.takeout("history", "role, content, tool_calls, tool_call_id", "user_id = ? AND group_id IS NULL", (user_id,))
        return history_text
    
    def takeout_tarot_history(self, user_id):
        tarot_history = self.takeout("tarot_history", "card_name, timestamp", "user_id = ?", (user_id,))
        return tarot_history