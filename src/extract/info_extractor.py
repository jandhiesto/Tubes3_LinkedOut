import re

def extract_name(text):
    # Coba cari nama di awal dokumen, biasanya 2-3 kata dengan huruf kapital
    match = re.search(r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})', text.strip())
    if match:
        return match.group(1)
    # Fallback jika tidak ada nama di awal
    return "Nama Tidak Ditemukan"

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
    # Cari bagian "Skills" atau "Accomplishments" dan ambil teks setelahnya
    # sampai menemukan baris kosong atau judul bagian baru
    match = re.search(r'(?:Skills|Accomplishments)\s*[:\n](.*?)(?:\n\n|\n[A-Z][a-z]+:)', text, re.IGNORECASE | re.DOTALL)
    if match:
        skills_text = match.group(1)
        # Ambil setiap kata atau frasa yang dipisahkan baris baru dan bersihkan
        skills = [skill.strip() for skill in skills_text.split('\n') if skill.strip()]
        return skills
    return []

def extract_experience(text):
    """
    Fungsi cerdas untuk mengekstrak riwayat pekerjaan.
    Mengembalikan list of dictionaries, di mana setiap dictionary adalah satu pekerjaan.
    """
    experience_list = []
    
    # 1. Isolasi blok teks "Experience" untuk menghindari salah ambil dari bagian lain
    experience_section_match = re.search(r'Experience\s*(.*)', text, re.DOTALL | re.IGNORECASE)
    if not experience_section_match:
        return []

    experience_text = experience_section_match.group(1)
    
    # 2. Buat pola Regex yang tangguh untuk menemukan setiap entri pekerjaan
    # Pola ini mencari: (Date Range) (Company) (Job Title) (Description)
    # Ia akan berhenti saat menemukan pola tanggal berikutnya atau akhir dari teks.
    pattern = re.compile(
        r'(\d{2}/\d{4}\s*-\s*\d{2}/\d{4})\s+'  # Grup 1: Tanggal (e.g., "09/2010 - 04/2011")
        r'([\w\s]+?)\s+'                      # Grup 2: Nama Perusahaan (non-greedy)
        r'City\s*,\s*State\s+'                # Membuang "City, State"
        r'(.+?)\n'                            # Grup 3: Jabatan (sampai akhir baris)
        r'((?:.+\n?)+?)'                      # Grup 4: Deskripsi (semua baris setelahnya)
        r'(?=\d{2}/\d{4}\s*-\s*|\Z)',          # Positive lookahead: berhenti sebelum tanggal berikutnya atau akhir string
        re.DOTALL
    )

    matches = pattern.findall(experience_text)

    for match in matches:
        job_entry = {
            'date_range': match[0].strip(),
            'company': match[1].strip(),
            'title': match[2].strip(),
            # Membersihkan deskripsi dari spasi berlebih dan baris kosong
            'description': '\n'.join([line.strip() for line in match[3].strip().split('\n') if line.strip()])
        }
        experience_list.append(job_entry)
        
    return experience_list

def extract_all_info(text):
    """
    Fungsi utama untuk memanggil semua extractor dan mengembalikan
    sebuah dictionary berisi informasi yang terstruktur.
    """
    # Bersihkan teks dari karakter aneh sebelum diproses
    cleaned_text = text.replace('ï¼​', ' ')

    return {
        'name': extract_name(cleaned_text),
        'email': extract_email(cleaned_text),
        'phone': extract_phone(cleaned_text),
        'skills': extract_skills(cleaned_text),
        'experience': extract_experience(cleaned_text) # Tambahkan hasil ekstraksi pengalaman
    }