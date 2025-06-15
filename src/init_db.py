# src/init_db.py

import os
import mysql.connector
from dotenv import load_dotenv, find_dotenv
from src.database_connector.db import connect_db

# 1) Paksa load .env (override jika ada env VAR di OS)
load_dotenv(find_dotenv(), override=True)

def create_database():
    host     = os.getenv("DB_HOST")
    user     = os.getenv("DB_USER")
    pwd      = os.getenv("DB_PASSWORD")
    db_name  = os.getenv("DB_NAME")

    print(f"[DEBUG] create_database() menggunakan: host={host}, user={user}, pwd={'***' if pwd else None}")
    # koneksi tanpa menyebut database
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
    # 2) Buat database dulu
    create_database()

    # 3) Connect ke database yang baru dibuat
    conn = connect_db()
    cursor = conn.cursor()
    print(f"[DEBUG] Menjalankan seeding SQL: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # eksekusi tiap statement
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
    # cari file seeding relatif terhadap file ini
    base_dir = os.path.dirname(__file__)
    sql_path = os.path.abspath(os.path.join(base_dir, "..", "data", "tubes3_seeding.sql"))
    run_sql_file(sql_path)
