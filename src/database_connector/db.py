import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',         
        database='cv_ats'
    )
    return conn

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

