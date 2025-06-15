import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

import mysql.connector

def connect_db():
    host     = os.getenv("DB_HOST")
    user     = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db       = os.getenv("DB_NAME")

    print(f"[DB] host={host}, user={user}, password={'***' if password else None}, db={db}")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db
    )
