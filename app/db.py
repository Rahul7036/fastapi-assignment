import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(DATABASE_URL)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    def call_add_call(self, code: str, unit: int, age: int, cost: float):
        self.connect()
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM add_call(%s, %s, %s, %s);", (code, unit, age, cost))
                result = cur.fetchone()
                self.conn.commit()
                return list(result) if result else None
        except Exception as e:
            self.conn.rollback()
            raise e

db = Database() 