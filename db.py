from dotenv import load_dotenv
import os
from mysql.connector import pooling

# Load .env variables
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE")
}

# Init db
pool = pooling.MySQLConnectionPool(pool_name="pool", pool_size=5, **DB_CONFIG)
def get_conn():
    return pool.get_connection()

# DB-Helper
def db_execute(sql, params=None, write=False):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=not write)
        cur.execute(sql, params or ())
        if write:
            conn.commit()
            return None
        return cur.fetchall()
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()
