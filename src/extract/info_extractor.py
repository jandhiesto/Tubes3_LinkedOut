# extract/info_extractor.py
import re

def extract_name(text):
    # Coba beberapa pola untuk menangkap nama
    # Pola 1: Dua kata dengan huruf kapital di awal teks
    match = re.search(r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})', text.strip())
    if match:
        return match.group(1).strip()
    
    # Pola 2: Cari header "Name"
    match = re.search(r'Name\s*[:\n]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
        
    return "Not Found"

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+62|08)\s*\d{2,4}\s*\d{4,8}', text)
    return match.group(0) if match else None

def extract_summary(text):
    # Cari di bawah heading "Summary", "Profile", atau "Overview"
    match = re.search(r'(?:Summary|Profile|Overview)\s*[:\n](.*?)(?:\n\n|\n[A-Z][a-z\s]+:)', text, re.IGNORECASE | re.DOTALL)
    if match:
        summary = match.group(1).strip()
        # Ganti baris baru ganda atau lebih dengan satu baris baru
        return re.sub(r'\s*\n\s*', ' ', summary)
    return "No summary found."

def extract_skills(text):
    match = re.search(r'(?:Skills|Accomplishments|Keahlian)\s*[:\n](.*?)(?:\n\n|\Z|Experience|Pendidikan)', text, re.IGNORECASE | re.DOTALL)
    if match:
        skills_text = match.group(1)
        # Pisahkan berdasarkan baris baru atau koma, bersihkan setiap item
        skills = re.split(r'\n|,', skills_text)
        return [skill.strip() for skill in skills if skill.strip()]
    return []

def extract_experience(text):
    experience_list = []
    # Pola yang lebih fleksibel, mencari kata kunci "Experience" atau "Pengalaman Kerja"
    exp_section_match = re.search(r'(Experience|Work Experience|Pengalaman Kerja)(.*)', text, re.IGNORECASE | re.DOTALL)
    if not exp_section_match:
        return []
    
    exp_text = exp_section_match.group(2)
    # Pola untuk setiap entri pekerjaan, mencari Jabatan, Perusahaan, dan Tanggal
    # Ini dibuat lebih umum untuk menangani format yang beragam
    pattern = re.compile(
        r'([A-Za-z\s]+)\n'          # Grup 1: Job Title (e.g., "Software Engineer")
        r'(.+?)\s*-\s*(.+)\n'       # Grup 2: Company Name
        r'(\w+\s+\d{4}\s*-\s*\w+\s+\d{4}|Present)', # Grup 3: Date Range (e.g., "May 2020 - Present")
        re.MULTILINE
    )
    
    # Fallback pattern jika formatnya berbeda
    # Anda bisa menambahkan lebih banyak pola di sini sesuai kebutuhan
    
    matches = re.findall(r'([A-Za-z\s,]+)\n(.*?)\n((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\s-\s(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}))', exp_text, re.IGNORECASE)

    for match in matches:
        job_entry = {
            'title': match[0].strip(),
            'company': match[1].strip(),
            'date_range': match[2].strip()
        }
        experience_list.append(job_entry)
        
    return experience_list

def extract_education(text):
    education_list = []
    # Cari bagian "Education" atau "Pendidikan"
    edu_section_match = re.search(r'(Education|Pendidikan)(.*)', text, re.IGNORECASE | re.DOTALL)
    if not edu_section_match:
        return []

    edu_text = edu_section_match.group(2)
    # Pola untuk setiap entri pendidikan
    matches = re.findall(r'([A-Za-z\s]+University.*?)\n(.*?)\n((?:\d{4}\s*-\s*\d{4}))', edu_text)
    
    for match in matches:
        edu_entry = {
            'institution': match[0].strip(),
            'degree': match[1].strip(),
            'date_range': match[2].strip()
        }
        education_list.append(edu_entry)
        
    return education_list

def extract_all_info(text, first_name, last_name):
    """
    Memanggil semua extractor dan mengembalikan dictionary terstruktur.
    """
    cleaned_text = text.replace('ï¼​', ' ')

    # Gunakan nama dari input sebagai fallback jika Regex gagal
    extracted_name = extract_name(cleaned_text)
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': extract_email(cleaned_text),
        'phone': extract_phone(cleaned_text),
        'summary': extract_summary(cleaned_text),
        'skills': extract_skills(cleaned_text),
        'experience': extract_experience(cleaned_text),
        'education': extract_education(cleaned_text)
    }

# NOTE: cv_extractor.py needs a slight modification to pass first_name and last_name
# to extract_all_info. This will be shown in the GUI section.