import os
import mysql.connector
from mysql.connector import Error
import dotenv; dotenv.load_dotenv()

class MSQL:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
    
        if self.connection.is_connected():
            print("Connected to MySQL Server")
        self.cursor = self.connection.cursor()

    def show_tables(self):
        self.cursor.execute("SHOW TABLES;")
        tables = self.cursor.fetchall()
        for table in tables:
            print(table[0])

    def get_n_rows(self, table_name):
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        return self.cursor.fetchone()[0]
    
    def show(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name};")
        return self.cursor.fetchall()
    
    def show_range(self, table_name, start, end):
        self.cursor.execute(f"""
                            SELECT * FROM {table_name}
                            WHERE log_id BETWEEN {start} AND {end};
                            """
                            )
        return self.cursor.fetchall()

    def log(self, username, firstname, lastname, input, chatbot):
        sql_insert_log = """
        INSERT INTO ChatLog (username, firstname, lastname, user_message, chatbot_response)
        VALUES (%s, %s, %s, %s, %s)
        """
        # Tuple with the values to be inserted
        log_data = (username, firstname, lastname, input, chatbot)

        # Execute the SQL command
        self.cursor.execute(sql_insert_log, log_data)   

        # Commit the transaction
        self.connection.commit()
        print("Chatbot activity logged successfully.")

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    