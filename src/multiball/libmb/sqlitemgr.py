import sqlite3
from typing import Optional

class SQLiteManager:
    def __init__(self, db_file):
        self.conn   = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self, create_statement):
        self.cursor.execute(create_statement)
        self.conn.commit()

    def insert_data(self, table_name: str, insert_data: dict) -> bool:
        insert_result = False
        try:
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['?'] * len(insert_data))
            values = tuple(insert_data.values())

            self.cursor.execute(f"""
                INSERT INTO {table_name}
                    ({columns})
                VALUES
                    ({placeholders})
                """,
                values
            )
            num_inserted = self.cursor.rowcount
            print(f"NUM INSERTED: {num_inserted}")
            if self.cursor.rowcount > 0:
                insert_result = True

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        print(f"Insert result: {insert_result}")
        return insert_result

    def query_data(self, query: str, args: list) -> list:
        self.cursor.execute(query, args)
        records = self.cursor.fetchall()
        return records

    def get_all_data(self, table_name: str) -> list:
        self.cursor.execute(f"SELECT * FROM {table_name}")
        records = self.cursor.fetchall()
        return records

    def update_data(self, query: str,  args: list) -> list:
        self.cursor.execute(query, args)
        self.conn.commit()
        return self.cursor.rowcount

    def close_connection(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()
