import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from .db import connect_db, execute_query

# Load environment variables
load_dotenv()

class QueryService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'cv_analyzer')
        }

    def get_applicant_by_cv_path(self, cv_path: str) -> Optional[Dict]:
        """
        Get applicant information by CV path.
        Returns None if no applicant is found with the given CV path.
        """
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        # Extract just the data/... part from the full path
        # Example: from "C:/Users/USER/Downloads/archive/data/data/CHEF/10001727.pdf"
        # to "data/CHEF/10001727.pdf"
        try:
            # Find the last occurrence of "data/" in the path
            data_index = cv_path.rindex("data/")
            db_path = cv_path[data_index:]  # Get everything from "data/" onwards
        except ValueError:
            # If "data/" not found, use the original path
            db_path = cv_path

        print(f"Looking up path in database: {db_path}")  # Debug print

        sql = """
            SELECT ap.*
            FROM ApplicantProfile ap
            JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            WHERE ad.cv_path = %s
        """
        cursor.execute(sql, (db_path,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        return row

def insert_applicant(first_name: str,
                     last_name: str,
                     dob: str,
                     address: str,
                     phone: str) -> int:
    """
    Masukkan data ApplicantProfile baru,
    return applicant_id (auto increment).
    """
    conn = connect_db()
    cursor = conn.cursor()

    sql = """
        INSERT INTO ApplicantProfile
            (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (first_name, last_name, dob, address, phone))
    new_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()
    return new_id

def insert_application_detail(applicant_id: int,
                              role: str,
                              cv_path: str) -> None:
    """
    Masukkan data ApplicationDetail untuk applicant_id tertentu.
    """
    conn = connect_db()
    cursor = conn.cursor()

    sql = """
        INSERT INTO ApplicationDetail
            (applicant_id, application_role, cv_path)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (applicant_id, role, cv_path))

    conn.commit()
    cursor.close()
    conn.close()

def get_all_applicants() -> list[dict]:
    """
    Ambil semua baris dari ApplicantProfile
    sebagai list of dict.
    """
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM ApplicantProfile")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def get_application_detail(applicant_id: int) -> list[dict]:
    """
    Ambil semua ApplicationDetail untuk applicant_id tertentu.
    """
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
          FROM ApplicationDetail
         WHERE applicant_id = %s
    """, (applicant_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows