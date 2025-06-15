from src.database_connector.db import connect_db

def save_raw_and_extracted(detail_id, raw, overview, skills, exp, edu):
    conn = connect_db()
    cur  = conn.cursor()
    sql = """
    UPDATE ApplicationDetail
       SET raw_text   = %s,
           overview   = %s,
           skills     = %s,
           experience = %s,
           education  = %s
     WHERE detail_id = %s
    """
    cur.execute(sql, (raw, overview, skills, exp, edu, detail_id))
    conn.commit()
    cur.close()
    conn.close()

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
