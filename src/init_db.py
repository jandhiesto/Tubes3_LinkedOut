import mysql.connector
from src.database_connector.db import connect_db

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicantProfile (
        applicant_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        date_of_birth DATE,
        address VARCHAR(255),
        phone_number VARCHAR(20)
    )
    """)

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

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database berhasil diinisialisasi.")

if __name__ == "__main__":
    init_db()
