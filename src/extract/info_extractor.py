import re

def extract_name(text):
    # Coba cari nama di awal dokumen, biasanya 2-3 kata dengan huruf kapital
    match = re.search(r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})', text.strip())
    if match:
        return match.group(1)
    return None

def extract_email(text):
    # Pola regex standar untuk email
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if match:
        return match.group(0)
    return None

def extract_phone(text):
    # Pola regex untuk nomor telepon (format Indonesia & internasional)
    match = re.search(r'(\+62|08)\d{8,12}', text)
    if match:
        return match.group(0)
    return None

def extract_skills(text):
    # Cari bagian "Skills" atau "Keterampilan" dan ambil teks setelahnya
    # sampai menemukan baris kosong atau judul bagian baru
    match = re.search(r'(?:Skills|Keterampilan|Kemampuan)\s*[:\n](.*?)(?:\n\n|\n[A-Z][a-z]+:)', text, re.IGNORECASE | re.DOTALL)
    if match:
        skills_text = match.group(1)
        # Ambil setiap kata atau frasa yang dipisahkan koma atau baris baru
        skills = [skill.strip() for skill in re.split(r'[,\n]', skills_text) if skill.strip()]
        return skills
    return []

def extract_all_info(text):
    """
    Fungsi utama untuk memanggil semua extractor dan mengembalikan
    sebuah dictionary berisi informasi yang terstruktur.
    """
    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text),
        # Anda bisa menambahkan fungsi untuk ekstraksi pendidikan, pengalaman kerja, dll.
    }