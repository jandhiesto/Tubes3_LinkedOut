# init_db.py
import mysql.connector
from database_connector.db import connect_db

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Hapus tabel jika ada untuk memastikan skema yang bersih (opsional, baik untuk development)
    cursor.execute("DROP TABLE IF EXISTS ApplicationDetail")
    cursor.execute("DROP TABLE IF EXISTS ApplicantProfile")

    # Membuat tabel ApplicantProfile yang lebih lengkap
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicantProfile (
        applicant_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email VARCHAR(255),
        phone_number VARCHAR(50),
        summary TEXT,
        skills TEXT,
        experience TEXT,
        education TEXT
    )
    """)
    print("✅ Table 'ApplicantProfile' created successfully.")

    # Membuat tabel ApplicationDetail
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicationDetail (
        detail_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        applicant_id INT NOT NULL,
        application_role VARCHAR(100),
        cv_path TEXT,
        FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
            ON DELETE CASCADE
    )
    """)
    print("✅ Table 'ApplicationDetail' created successfully.")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database successfully initialized.")

if __name__ == "__main__":
    init_db()