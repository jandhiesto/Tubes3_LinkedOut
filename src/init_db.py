import os
import mysql.connector
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

def create_database():
    host     = os.getenv("DB_HOST")
    user     = os.getenv("DB_USER")
    pwd      = os.getenv("DB_PASSWORD")
    db_name  = os.getenv("DB_NAME")

    print(f"[DEBUG] create_database() menggunakan: host={host}, user={user}, pwd={'***' if pwd else None}")
    cnx = mysql.connector.connect(
        host=host,
        user=user,
        password=pwd
    )
    cur = cnx.cursor()
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    cnx.commit()
    cur.close()
    cnx.close()
    print(f"[OK] Database `{db_name}` siap (dibuat jika belum ada).")

def run_sql_file(path: str):
    create_database()

    # Create database config
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }

    # Import here to avoid circular import
    from database_connector.db import connect_db
    conn = connect_db(db_config)
    cursor = conn.cursor()
    print(f"[DEBUG] Menjalankan seeding SQL: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()

    for stmt in sql.split(';'):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as err:
            print(f"[ERROR] Gagal eksekusi: {stmt[:80]}…\n   → {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] Tabel & data seed berhasil dibuat.")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    sql_path = os.path.abspath(os.path.join(base_dir, "..", "data", "tubes3_seeding.sql"))
    run_sql_file(sql_path)
