from .db import connect_db

def insert_applicant(first_name, last_name, dob, address, phone):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (first_name, last_name, dob, address, phone))
    applicant_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()

    return applicant_id

def insert_application_detail(applicant_id, role, cv_path):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (applicant_id, role, cv_path))

    conn.commit()
    cursor.close()
    conn.close()

def get_all_applicants():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM ApplicantProfile")
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

def get_application_detail(applicant_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM ApplicationDetail
        WHERE applicant_id = %s
    """, (applicant_id,))
    
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result
