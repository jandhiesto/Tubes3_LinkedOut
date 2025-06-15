# database_connector/query_service.py
from .db import connect_db
import json

def insert_full_applicant(profile_data, role, cv_path):
    """
    Menyisipkan profil pelamar lengkap dan detail aplikasi dalam satu transaksi.
    """
    conn = connect_db()
    cursor = conn.cursor()

    profile_query = """
        INSERT INTO ApplicantProfile (first_name, last_name, email, phone_number, summary, skills, experience, education)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Mengonversi list/dict ke JSON string untuk disimpan di DB
    skills_json = json.dumps(profile_data.get('skills', []))
    experience_json = json.dumps(profile_data.get('experience', []))
    education_json = json.dumps(profile_data.get('education', []))

    profile_values = (
        profile_data.get('first_name'),
        profile_data.get('last_name'),
        profile_data.get('email'),
        profile_data.get('phone'),
        profile_data.get('summary'),
        skills_json,
        experience_json,
        education_json
    )
    
    cursor.execute(profile_query, profile_values)
    applicant_id = cursor.lastrowid

    detail_query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
        VALUES (%s, %s, %s)
    """
    cursor.execute(detail_query, (applicant_id, role, cv_path))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return applicant_id

def get_all_applicants_with_details():
    """
    Mengambil semua data pelamar beserta detail aplikasi mereka.
    """
    conn = connect_db()
    # dictionary=True membuat cursor mengembalikan hasil sebagai dict
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            p.applicant_id,
            p.first_name,
            p.last_name,
            p.email,
            p.phone_number,
            p.summary,
            p.skills,
            p.experience,
            p.education,
            d.application_role,
            d.cv_path
        FROM
            ApplicantProfile p
        JOIN
            ApplicationDetail d ON p.applicant_id = d.applicant_id
        ORDER BY
            p.first_name, p.last_name
    """
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # Dekode field JSON kembali menjadi objek Python
    for row in results:
        try:
            row['skills'] = json.loads(row['skills']) if row['skills'] else []
            row['experience'] = json.loads(row['experience']) if row['experience'] else []
            row['education'] = json.loads(row['education']) if row['education'] else []
        except (json.JSONDecodeError, TypeError):
            # Fallback jika data tidak dalam format JSON yang valid
            row['skills'] = []
            row['experience'] = []
            row['education'] = []
            
    return results